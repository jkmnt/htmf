from __future__ import annotations

import html
import logging
import re
import typing as t

import html5lib
import html5lib.html5parser

from pylint.checkers import BaseChecker, utils


from astroid import (
    AnnAssign,
    Arguments,
    Assign,
    AssignName,
    Attribute,
    BoolOp,
    BinOp,
    Call,
    Const,
    FormattedValue,
    FunctionDef,
    IfExp,
    Import,
    ImportFrom,
    JoinedStr,
    Module,
    Name,
    NodeNG,
    Subscript,
)

from astroid.context import InferenceContext


if t.TYPE_CHECKING:
    from pylint.lint import PyLinter

logger = logging.getLogger(__name__)

CHECKER_ID = 81

parser = html5lib.HTMLParser(strict=True)

ALLOWED_VALS = (Call, Const, IfExp, Name, BoolOp)


def extract_func_name(call: Call):
    """Extract name or name.attribute from function call"""
    node = call.func
    if isinstance(node, Name):
        return node.name
    if isinstance(node, Attribute) and isinstance(node.expr, Name):
        return f"{node.expr.name}.{node.attrname}"
    return None


def extract_anno_types(node: NodeNG) -> list[str | None]:
    """Extract annotation types, expecting it to be the union in general case. The None treated as a special case to support none_is_ok flag"""
    if isinstance(node, BinOp) and node.op == "|":
        left = extract_anno_types(node.left)
        right = extract_anno_types(node.right)
        if left and right:
            return left + right
        return []
    if isinstance(node, Subscript):
        node = node.value
    if isinstance(node, Name):
        return [node.name]
    if isinstance(node, Attribute) and isinstance(node.expr, Name):
        return [f"{node.expr.name}.{node.attrname}"]
    if isinstance(node, Const) and node.value is None:
        return [None]
    return []


def extract_arg_types(assign: AssignName, args: Arguments):
    """Try to extract the type annotation for the argument"""
    all_args = (args.args or []) + args.posonlyargs + args.kwonlyargs
    all_annos = args.annotations + args.posonlyargs_annotations + args.kwonlyargs_annotations
    idx = all_args.index(assign)
    if idx >= 0:
        anno = all_annos[idx]
        return extract_anno_types(anno) if anno else []
    return []


def extract_scopes_comment(node: NodeNG, code: list[str]):
    """
    Extract magic htmf-scopes=... comment from the preceeding line.
    Example:
        # htmf-scopes=html,table,tbody

    These scopes are used to artificially wrap the markup and make it valid for html5 strict parsing.
    Otherwise the html5lib will complain for the orphaned <tr> tags etc.

    """
    assert node.lineno
    s = code[node.lineno - 1]
    s = s.strip()
    if not s.startswith("#"):
        return []
    s = s[1:]
    parents_match = re.search(r"htmf-scopes=([\w,]+)", s)
    if parents_match:
        scopes = parents_match.groups()[0].split(",")
        scopes = [s for s in scopes if s]
        return scopes[::-1]
    return []


def infer_single(node: NodeNG, name: str):
    context = InferenceContext()
    context.lookupname = name
    infs = list(node.infer(context))
    return infs[0] if len(infs) == 1 else None


def lookup_single(node: NodeNG, name: str):
    scope_, assigns = node.scope().lookup(name)
    if len(assigns) != 1:
        return None
    return assigns[0]


def resolve_funcdef(call: Call):
    if isinstance(call.func, Name):
        # Simple name format.
        # Lookup may resolve to the function in this module or import.
        # In case of import use infer() to load module(s) and locate the terminating funcdef
        node = lookup_single(call, call.func.name)
        if isinstance(node, (Import, ImportFrom)):
            node = infer_single(node, call.func.name)
        return node if isinstance(node, FunctionDef) else None

    if isinstance(call.func, Attribute) and isinstance(call.func.expr, Name):
        # Attribute.Name
        # Assume it's the imported function.
        # We do not allow local definitions, otherwise we stuck in the rabbit hole of classes/attributes etc
        module_name_maybe = call.func.expr.name
        node = lookup_single(call, module_name_maybe)
        if not isinstance(node, (Import, ImportFrom)):
            return None
        node = infer_single(node, module_name_maybe)
        if not isinstance(node, Module):
            return None
        # module was found. now lookup the function.
        # It may be the function of the module or reexport (in this case infer again)
        node = lookup_single(node, call.func.attrname)
        if isinstance(node, FunctionDef):
            return node
        if node:
            node = infer_single(node, call.func.attrname)
            return node if isinstance(node, FunctionDef) else None

    return None


# typing magic from official python docs
def trace_calls[T, **P](f: t.Callable[P, T]) -> t.Callable[P, T]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        # arg0 is self
        me: t.Any = args[0]
        if not hasattr(me, "_nest"):
            me._nest = 0
        me._nest += 1
        logger.debug(" " * me._nest * 2 + f.__name__)
        try:
            return f(*args, **kwargs)
        finally:
            me._nest -= 1

    return inner


class ExprChecker:
    """
    This is class instead of the simple module-level functions to have common config.
    """

    def __init__(self, *, safe_type: t.Pattern, allow_gettext=True, whitelisted_funcs: t.Pattern | None):
        self._whitelisted_funcs = whitelisted_funcs
        self._safe_type = safe_type
        self.allow_gettext = allow_gettext

    def check(self, fv: FormattedValue):
        logger.info(f"Checking expression '{fv.as_string()}'")
        value = fv.value
        if isinstance(value, ALLOWED_VALS) and self.is_val_resolves_to_safe(value, none_is_ok=False):
            return True
        return False

    @trace_calls
    def is_safe_func_call(self, call: Call, *, none_is_ok: bool):
        """
        Check if call to the function is known to be safe or type-annotated as safe.
        The call may resolve to the function in same module or imported function.
        """

        if self.is_whitelisted_call(call):
            return True
        if self.allow_gettext and self.is_simple_gettext_call(call):
            return True

        funcdef = resolve_funcdef(call)
        if funcdef and self.is_returning_safe(funcdef, none_is_ok=none_is_ok):
            logger.info(f"{funcdef.qname()} -> Safe")
            return True
        return False

    def is_returning_safe(self, funcdef: FunctionDef, *, none_is_ok: bool):
        return funcdef.returns and self.is_safetype(extract_anno_types(funcdef.returns), none_is_ok=none_is_ok)

    @trace_calls
    def is_simple_gettext_call(self, call: Call):
        """
        Check if call to the simple non-interpolated gettext with safe literal.
        Assuming the translations are sane and contain no unsafe characters too.
        This is a wrong assumption, but wrapping all gettext calls creates too much noise.
        The unescaped static translations should be very noticeable and easy to fix.
        """

        name = extract_func_name(call)

        if name in ("_", "gettext"):
            arglen = 1
            argpos = 0
        elif name in ("pgettext",):
            arglen = 2
            argpos = 1
        else:
            return False

        return (
            len(call.args) == arglen
            and isinstance(arg := call.args[argpos], Const)
            and not call.keywords
            and html.escape(arg.value) == arg.value
        )

    @trace_calls
    def is_whitelisted_call(self, call: Call):
        """
        Check if call is in the static whitelist
        """
        if self._whitelisted_funcs:
            name = extract_func_name(call)
            if not name:
                return False
            return bool(self._whitelisted_funcs.fullmatch(name))
        return False

    @trace_calls
    def is_safe_literal(self, const: Const, none_is_ok: bool):
        constant = const.value
        if none_is_ok and constant is None:
            return True
        if not isinstance(constant, str):
            return False
        return html.escape(constant) == constant

    def is_safetype(self, type: list[str | None], *, none_is_ok: bool):
        """Check if all types in type annotation is safe (or None is none_is_ok)"""
        if not type:
            return False
        if none_is_ok:
            return all(tp is None or self._safe_type.fullmatch(tp) for tp in type)
        else:
            return all(tp and self._safe_type.fullmatch(tp) for tp in type)

    @trace_calls
    def is_assignname_resolves_to_safe(self, assign: AssignName, *, none_is_ok: bool):
        """Check if name assignment resolves to safe.
        The supported assignments are:
            - normal assign (result of call, const, etc): follow the chain
            - name is defined in function arguments: check if argument is typehinted as safe
            - assign (var creation) with type annotation: check if annotated as safe
        """

        parent = assign.parent

        if isinstance(parent, Assign):
            return isinstance(parent.value, ALLOWED_VALS) and self.is_val_resolves_to_safe(parent.value, none_is_ok=none_is_ok)
        if isinstance(parent, Arguments):
            return self.is_safetype(extract_arg_types(assign, parent), none_is_ok=none_is_ok)
        if isinstance(parent, AnnAssign):
            return self.is_safetype(extract_anno_types(parent.annotation), none_is_ok=none_is_ok)
        return False

    @trace_calls
    def is_name_resolves_to_safe(self, name: Name, *, none_is_ok: bool):
        """Check if all assignments to name in scope (if/elif/else branches etc) resolves to safe"""
        # astroid magic !
        varname = name.name
        scope_, assigns = name.scope().lookup(varname)
        if not assigns:
            return False
        return all(
            (isinstance(assign, AssignName) and self.is_assignname_resolves_to_safe(assign, none_is_ok=none_is_ok)) for assign in assigns
        )

    @trace_calls
    def is_val_resolves_to_safe(self, value: Call | Const | IfExp | Name | BoolOp, none_is_ok: bool):
        """Check if value(variable) is safe
        A few simple cases are supported:
            - variable is terminated in call: check if call brings safety
            - variable is const: check if const is safe
            - variable is if ... else ... expression: both branches must be safe
            - variable is a 'or' b expression: left expression may by safe or None, the last expr must be safe
            - variable is name: follow name assignment with possible recursion
        """

        if isinstance(value, Call):
            return self.is_safe_func_call(value, none_is_ok=none_is_ok)
        if isinstance(value, Const):
            return self.is_safe_literal(value, none_is_ok=none_is_ok)
        if isinstance(value, IfExp):
            return (
                isinstance(value.body, ALLOWED_VALS)
                and self.is_val_resolves_to_safe(value.body, none_is_ok=none_is_ok)
                and isinstance(value.orelse, ALLOWED_VALS)
                and self.is_val_resolves_to_safe(value.orelse, none_is_ok=none_is_ok)
            )
        if isinstance(value, BoolOp) and value.op == "or":
            if len(value.values) < 2:
                return False
            *lefts, last = value.values
            return (
                all(isinstance(left, ALLOWED_VALS) and self.is_val_resolves_to_safe(left, none_is_ok=True) for left in lefts)
                and isinstance(last, ALLOWED_VALS)
                and self.is_val_resolves_to_safe(last, none_is_ok=none_is_ok)
            )
        if isinstance(value, Name):
            return self.is_name_resolves_to_safe(value, none_is_ok=none_is_ok)
        return False


class HtmfChecker(BaseChecker):
    name = "htmf-checker"
    msgs = {
        f"E{CHECKER_ID}01": (
            "Bad HTML markup. %s",
            "htmf-bad-markup",
            "Markup parse error as reported by html5lib",
        ),
        f"W{CHECKER_ID}02": (
            "f-expression '%s' is probably HTML-unsafe",
            "htmf-unsafe-fexpression",
            "f-expressions in HTML templates should have Safe type. "
            "They may be the Safe-annotated variables or Safe-annotated function calls",
        ),
    }
    options = (
        (
            "htmf-markup-func",
            {
                "default": r"htmf\.m|htmf\.markup|ht\.m|ht\.markup",
                "type": "regexp",
                "metavar": "<regexp>",
                "help": "Function wrapping the HTML fragment",
            },
        ),
        (
            "htmf-document-func",
            {
                "default": r"htmf\.document|ht\.document",
                "type": "regexp",
                "metavar": "<regexp>",
                "help": "Function wrapping the HTML document",
            },
        ),
        (
            "htmf-safetype",
            {
                "default": r"htmf\.SafeOf|ht\.SafeOf|SafeOf|htmf\.Safe|ht\.Safe|Safe",
                "type": "regexp",
                "metavar": "<regexp>",
                "help": "Type annotating the function return type, variable or argument as HTML-safe",
            },
        ),
        (
            "htmf-safe-func",
            {
                "default": None,
                "type": "regexp",
                "metavar": "<regexp>",
                "help": "Whitelist of safe functions",
            },
        ),
        (
            "htmf-allow-simple-gettext",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Treat simple non-interpolated gettext calls as safe",
            },
        ),
        (
            "htmf-allow-flat-markup",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Allow markup of multiple elements without the parent",
            },
        ),
    )

    _sources: t.ClassVar[dict[str, list[str]]] = {}

    def __init__(self, linter: PyLinter):
        # logging.basicConfig(level="INFO")
        super().__init__(linter)

    def open(self) -> None:
        config = self.linter.config
        self._markup_func: t.Pattern = config.htmf_markup_func
        self._document_func: t.Pattern = config.htmf_document_func
        self.expr_checker = ExprChecker(
            safe_type=config.htmf_safetype,
            allow_gettext=config.htmf_allow_simple_gettext,
            whitelisted_funcs=config.htmf_safe_func,
        )

        return super().open()

    def _update_src_cache(self, file: str):
        if file not in self._sources:
            with open(file, encoding="utf-8") as f:
                self._sources[file] = [""] + f.readlines()  # linenumbers are starting from 1, add empty line
        return self._sources[file]

    @utils.only_required_for_messages(
        "htmf-bad-markup",
        "htmf-unsafe-fexpression",
    )
    def visit_call(self, call: Call):
        name = extract_func_name(call)

        if not name:
            return
        if not (self.is_markup_func(name) or self.is_document_func(name)):
            return
        if not call.args:
            return

        markup_node = call.args[0]

        if isinstance(markup_node, JoinedStr) or (isinstance(markup_node, Const) and isinstance(markup_node.value, str)):
            file = call.root().file
            logger.info(f"Checking markup {file}:{markup_node.lineno}")
            scopes = extract_scopes_comment(call, self._update_src_cache(file)) if file else []
            self.check_markup(markup_node, scopes, is_document=self.is_document_func(name))

            if isinstance(markup_node, JoinedStr):
                for fv in markup_node.values:
                    if isinstance(fv, FormattedValue):
                        if not self.expr_checker.check(fv):
                            self.add_message(msgid="htmf-unsafe-fexpression", args=fv.as_string(), node=fv)

    def is_markup_func(self, name: str):
        return bool(self._markup_func.fullmatch(name))

    def is_document_func(self, name: str):
        return bool(self._document_func.fullmatch(name))

    # checker stuff
    def check_markup(self, node: JoinedStr | Const, scopes: list[str], *, is_document=False):
        """
        Check HTML markup by parsing it by html5lib in strict mode.
        If markup is f-string, the substitutions are replaced by whitespaces
        """
        if isinstance(node, JoinedStr):
            text = " ".join(s.value for s in node.values if isinstance(s, Const))
        else:
            assert isinstance(node.value, str)
            text = node.value

        for scope in scopes:
            text = f"<{ scope }>{ text }</{ scope }>"

        try:
            if is_document:
                parser.parse(text)
            else:
                elements = parser.parseFragment(text)
                if elements is None or len(elements) == 0:
                    self.add_message(msgid="htmf-bad-markup", args="No elements found", node=node)
                elif len(elements) != 1 and not self.linter.config.htmf_allow_flat_markup:
                    self.add_message(msgid="htmf-bad-markup", args="Multiple elements found", node=node)
        except html5lib.html5parser.ParseError as e:
            self.add_message(msgid="htmf-bad-markup", args=f"[html5lib: {e}]", node=node)
        except Exception as e:
            self.add_message(msgid="htmf-bad-markup", args=f"[Parse error {e}]", node=node)
