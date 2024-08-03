import re
import typing as t

from .formatter import FragmentFormatter, Fragment
from ._vendor.htmlbeautifier.html.beautifier import Beautifier


def get_js_formatter(args: t.Any, *, trigger: re.Pattern[str]):

    import jsbeautifier

    def _beautify(s: str, _dummy: t.Any = None):
        return jsbeautifier.beautify(s, args)

    def _formatter(frag: Fragment):
        if frag.is_singleline:
            return frag.code
        return _beautify(frag.code)

    return (
        FragmentFormatter(
            trigger=trigger,
            formatter=_formatter,
            escapes=("", ""),
            applies_to="c",
        ),
        _beautify,
    )


def get_css_formatter(args: t.Any, *, trigger: re.Pattern[str]):
    import cssbeautifier

    def _beautify(s: str, _dummy: t.Any = None):
        return cssbeautifier.beautify(s, args)

    def _formatter(frag: Fragment):
        if frag.is_singleline:
            return frag.code
        return _beautify(frag.code)

    return (
        FragmentFormatter(
            trigger=trigger,
            formatter=_formatter,
            escapes=("", ""),
            applies_to="c",
        ),
        _beautify,
    )


def get_html_formatter(
    args: t.Any,
    *,
    trigger: re.Pattern[str],
    js_beautifier: t.Callable[[str, t.Any], str] | None,
    css_beautifier: t.Callable[[str, t.Any], str] | None,
):
    def _formatter(frag: Fragment):
        if frag.is_singleline:
            return frag.code

        return Beautifier(
            frag.code,
            args,
            # interpolate embedded js/html only if non-templated. otherwise there are too many conflicting cases with braces
            js_beautifier=None if frag.expressions else js_beautifier,
            css_beautifier=None if frag.expressions else css_beautifier,
        ).beautify()

    return FragmentFormatter(
        trigger=trigger,
        formatter=_formatter,
        escapes=("{#", "#}"),
    )
