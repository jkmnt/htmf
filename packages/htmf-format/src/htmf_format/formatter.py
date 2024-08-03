from dataclasses import dataclass
import re
import typing as t

import ast
from ast import FormattedValue, Module, NodeVisitor, Call, JoinedStr, Constant

from .astcheck import simplify_and_stringify
from .utils import Linemap, compose_linemap, extract_name, node_to_pos
from .output import err


class FragmentFormatter:
    def __init__(
        self,
        trigger: re.Pattern[str] | str,
        formatter: t.Callable[["Fragment"], str],
        escapes: tuple[str, str],
        trim_head=True,
        trim_tail=True,
        #  f = f-string, c = constant, fc = both
        applies_to: t.Literal["f", "c", "fc"] = "fc",
    ):

        self.trigger = re.compile(trigger) if isinstance(trigger, str) else trigger
        self.formatter = formatter
        self.escapes = escapes
        self.applies_to = applies_to

        s_esc, e_esc = escapes

        # precalculate some regexps
        head = r"(?:\s*\\)?(?:\n)?" if trim_head else r"(?:\s*\\)?"
        tail = r"(?:\s*)" if trim_tail else ""
        self.frag_re = re.compile(rf"""^(?:r)?(?:f)?(\"\"\"|'''|\"|'){ head }(.*?){ tail }(\1)$""", re.DOTALL | re.IGNORECASE)
        self.preprocess_re = re.compile(r"(\ue000.*?\ue001)", flags=re.DOTALL)
        self.postprocess_re = re.compile(f"({re.escape(s_esc) }.*?{re.escape(e_esc)})", flags=re.DOTALL)


def positional_replace(pat: re.Pattern, string: str, items: t.Sequence[str]):
    its = list(items)

    def _replace(_m: re.Match):
        repl = its.pop(0)
        return repl

    res = pat.sub(_replace, string)
    assert not its, "Some fragments were not replaced"
    return res


def is_ignored(node: Call, linemap: Linemap):
    lineno = node.lineno - 1
    if lineno < 1:
        return False
    prev = linemap[lineno - 1][1].decode()
    prev = prev.strip()
    if not prev.startswith("#"):
        return False
    return "htmf-nofmt" in prev


@dataclass
class Fragment:
    begin: int
    end: int
    code: str
    is_multiline: bool
    formatter: FragmentFormatter
    expressions: list[str] | None = None

    @property
    def is_singleline(self):
        return not self.is_multiline


class Document(NodeVisitor):
    def __init__(self, formatters: t.Sequence[FragmentFormatter], src: str, linemap: Linemap, root: ast.AST) -> None:
        self.formatters = formatters
        self.src = src
        self.linemap = linemap
        self.fragments: list[Fragment] = []
        self.root = root

    def visit_Call(self, node: Call):
        name = extract_name(node)
        more = True
        if name and node.args and not is_ignored(node, self.linemap):
            for f in self.formatters:
                if not more:
                    break
                if f.trigger.fullmatch(name):
                    if isinstance(node.args[0], Constant) and isinstance(node.args[0].value, str) and "c" in f.applies_to:
                        self.handle_literal(node.args[0], formatter=f)
                        more = False
                    elif isinstance(node.args[0], JoinedStr) and "f" in f.applies_to:
                        self.handle_template(node.args[0], formatter=f)
                        more = False
        #
        if more:
            self.generic_visit(node)

    def create_fragment(self, node: ast.AST, *, src: str, formatter: FragmentFormatter, expressions: list[str] | None = None):
        b, e = node_to_pos(node, self.linemap)

        m = formatter.frag_re.match(src[b:e])
        if not m:
            err("Failed to create fragment")
            return None

        b_offset, e_offset = m.span(2)
        b += b_offset
        e = b + e_offset - b_offset
        assert b <= e

        is_multiline = m.group(1) in ("'''", '"""')

        return Fragment(begin=b, end=e, code=src[b:e], is_multiline=is_multiline, expressions=expressions, formatter=formatter)

    def handle_literal(self, node: Constant, *, formatter: FragmentFormatter):
        frag = self.create_fragment(node, src=self.src, formatter=formatter)
        if not frag:
            return
        self.fragments.append(frag)

    def handle_template(self, node: JoinedStr, *, formatter: FragmentFormatter):
        expressions: list[str] = []

        # process expressions as embedded documents
        for expr in node.values:
            if isinstance(expr, FormattedValue):
                inner = Document(self.formatters, src=self.src, linemap=self.linemap, root=expr).process()
                expressions.append(inner)

        # Patch source: replace expression with reserved unicodes wrapping the content replaced with *
        # This will preserve the offsets.
        # XXX: it's ugly. is there the better way ?
        patched_src = self.src

        for expr in node.values:
            if isinstance(expr, FormattedValue):
                b, e = node_to_pos(expr, self.linemap)
                assert e - b >= 2
                chunk = patched_src[b + 1 : e - 1]
                placeholder = re.sub(".", "*", chunk)
                if True:
                    assert len(chunk) == len(placeholder)
                    assert len(chunk.splitlines()) == len(placeholder.splitlines())
                patched_src = f"{ patched_src[:b] }\ue000{ placeholder }\ue001{ patched_src[e:] }"

        frag = self.create_fragment(node, src=patched_src, expressions=expressions, formatter=formatter)
        if not frag:
            return

        # Now offsets are accounted for. Update patched source again with content wrapped in escapes with all characters replaced by *.
        # This will attempt to preserve the shape.
        s_esc, e_esc = formatter.escapes
        placeholders = [f"{ s_esc }{ re.sub('.', '*', exp[len(s_esc):-len(e_esc)]) }{ e_esc }" for exp in expressions]
        frag.code = positional_replace(formatter.preprocess_re, frag.code, placeholders)
        self.fragments.append(frag)

    def get_fragments(self):
        b, e = node_to_pos(self.root, self.linemap) if not isinstance(self.root, Module) else (0, None)
        pos = b
        for f in self.fragments:
            yield self.src[pos : f.begin]
            yield f
            pos = f.end
        yield self.src[pos:e]

    def process(self):
        # quick check if src need processing at all
        if not any(f.trigger.search(self.src) for f in self.formatters):
            return self.src

        self.visit(self.root)

        res: list[str] = []
        for part in self.get_fragments():
            if isinstance(part, str):
                res.append(part)
            else:
                processed = part.formatter.formatter(part)
                if part.expressions:
                    processed = positional_replace(part.formatter.postprocess_re, processed, part.expressions)
                res.append(processed)

        out = "".join(res)
        return out


def process(src: str, formatters: t.Sequence[FragmentFormatter], *, verify_ast=True):
    if "\ue000" in src or "\ue001" in src:
        raise Exception(r"Source shouldn't contain chars \ue000, \ue001")

    linemap = compose_linemap(src)

    root = ast.parse(src)

    res = Document(formatters=formatters, linemap=linemap, src=src, root=root).process()

    if verify_ast:
        a_text = simplify_and_stringify(root, formatters)
        b_text = simplify_and_stringify(ast.parse(res), formatters)
        assert a_text == b_text, "AST changed"

    return res
