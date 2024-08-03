from __future__ import annotations

import ast
import re
import typing as t

from ast import Module, NodeTransformer, Call, JoinedStr, Constant

from .utils import extract_name

if t.TYPE_CHECKING:
    from .formatter import FragmentFormatter


# Simplify the formatted parts in AST by removing all whitespaces and line breaks.
# for python runtime they are just the constants. Then we could compare ast by unparsing it to string.
# It's not very robust
class FlattenConstants(NodeTransformer):
    def __init__(self, formatters: t.Sequence[FragmentFormatter]) -> None:
        self.formatters = formatters

    def visit_Call(self, node: Call):
        gvres = self.generic_visit(node)
        if gvres is None:
            return None
        assert isinstance(gvres, Call)
        node = gvres

        name = extract_name(node)
        if name and node.args:
            for f in self.formatters:
                if not f.trigger.fullmatch(name):
                    continue
                if isinstance(node.args[0], Constant) and isinstance(node.args[0].value, str) and "c" in f.applies_to:
                    gvres = self.handle_literal(node.args[0])
                    if gvres is None:
                        del node.args[0]
                    else:
                        node.args[0] = gvres
                    break
                if isinstance(node.args[0], JoinedStr) and "f" in f.applies_to:
                    values = []
                    for v in node.args[0].values:
                        if isinstance(v, Constant):
                            v = self.handle_literal(v)
                        else:
                            v = self.generic_visit(v)
                        if v is not None:
                            values.append(v)
                    node.args[0].values = values
                    break
        return node

    def handle_literal(self, node: Constant):
        assert isinstance(node.value, str)
        node.value = re.sub(r"\s", "", node.value)
        # completely remove the empty nodes
        return node if node.value else None


def simplify_and_stringify(module: Module, formatters: t.Sequence[FragmentFormatter]):
    res = FlattenConstants(formatters).visit(module)
    return ast.unparse(res)
