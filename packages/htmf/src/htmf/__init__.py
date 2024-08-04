"""htmf: Python f-strings HTML templating library"""

# Licenced under the MIT License: https://www.opensource.org/licenses/mit-license.php

__version__ = "0.2.0"


from typing import Mapping, Iterable, TypeVar, Annotated, Any

import re
import json as _json
from html import unescape


__all__ = [
    "attr",
    "Attrs",
    "c",
    "classname",
    "csv_attr",
    "document",
    "handler",
    "json_attr",
    "m",
    "mark_as_safe",
    "markup",
    "Safe",
    "SafeOf",
    "script",
    "style",
    "stylesheet",
    "t",
    "text",
]


Arg = str | bool | None | int | float
Attrs = Mapping[str, Arg]
CnArg = str | bool | None

S = TypeVar("S", bound="Safe")
SafeOf = Annotated[S, "safe"]
"""Generic annotation to mark NewType(T, Safe) as safe for linter"""


_INT_OR_FLOAT = (int, float)
_REPLACE_RE = re.compile(r"""[&<>"']""")


def _replacer(m: re.Match[str]):
    return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[m[0]]


# The re.sub is very fast and won't call _replacer until strictly needed.
# Moreover, most strings would not require escaping and re.sub will return the original string
# avoiding extra mem allocation.
def _html_escape(s: str) -> str:
    return _REPLACE_RE.sub(_replacer, s)


class Safe(str):
    """
    Noop class for marking the string as HTML-safe.
    Used for marking strings safe and preventing double escape at runtime.
    Used for type annotations.

    Not intended to be instantiated outside of the library code !
    """

    def unescape(self) -> str:
        return unescape(self)


def mark_as_safe(s: str) -> Safe:
    """
    Mark the string as safe, promoting it to the Safe class.
    Escape hatch if you really need to include some not-to-be esscaped string.
    """
    return Safe(s)


def escape(s: str) -> Safe:
    """HTML-escape the string making it safe for inclusion in the markup"""
    return s if isinstance(s, Safe) else Safe(_html_escape(s))


def markup(s: str) -> Safe:
    """
    Strips the whitespaces and marks the string as safe.
    Triggers the HTML-syntax highlight
    """
    return Safe(s.strip())


def text(*args: Arg | Iterable[Arg], sep="") -> Safe:
    """
    Basic building block for HTML texts and fragments.

    The arguments may be `None` | `str` | `bool` | `int` | `float` or iterables of such types.
    Supplied values are flattened into the one single list.
    Nones and bools are dropped as in JSX. Numbers are stringified.
    Strings are escaped unless marked as safe.

    Returns the single string of values joined.
    """

    # unrolled and inlined to squieeze the marginal extra performance

    toks: list[str] = []

    append = toks.append
    esc = _html_escape
    isinst = isinstance
    safe = Safe
    number = _INT_OR_FLOAT
    _str = str

    for arg in args:
        if arg is True or arg is False or arg is None:
            pass
        elif isinst(arg, safe):
            append(arg)
        elif isinst(arg, _str):
            append(esc(arg))
        elif isinst(arg, number):  # rendered numbers should contain no html-unsafe chars
            append(_str(arg))
        else:  # must be iterable
            try:
                for sub in arg:
                    if sub is True or sub is False or sub is None:
                        pass
                    elif isinst(sub, safe):
                        append(sub)
                    elif isinst(sub, _str):
                        append(esc(sub))
                    elif isinst(sub, number):
                        append(_str(sub))
            except TypeError:
                pass

    return safe(sep.join(toks))


def attr(arg: Attrs | None = None, /, **kwargs: Arg) -> Safe:
    """
    Accepts the dictionary of name-value pairs and/or name-value keywords.
    Keywords override the dictionary.
    Formats the result as the quoted HTML-attributes suitable for direct inclusion into the tags.

    - `True` values are rendered as just the name, e.g `hidden`
    - `False` values are discarded
    - string values are rendered as name-value pairs, e.g. `type = "checkbox"`
    - number values are interpolated, e.g. `tabindex="-1"`

    Return the single string of whitespace-separated pairs.
    """

    args = (arg or {}) | kwargs

    keyvals: list[str] = []

    append = keyvals.append
    esc = _html_escape
    isinst = isinstance
    safe = Safe
    number = _INT_OR_FLOAT

    for k, v in sorted(args.items()):
        if v is None or v is False:
            pass
        else:
            if not isinst(k, safe):
                k = esc(k)
            k = k.strip()

            if not k:  # special catch for the empty key
                pass
            elif v is True:  # boolean attribute e.g. 'hidden', 'disabled'
                append(k)
            elif isinst(v, safe):
                append(f'{ k }="{ v }"')
            elif isinst(v, str):
                append(f'{ k }="{ esc(v) }"')
            elif isinst(v, number):
                append(f'{ k }="{ v }"')

    return safe(" ".join(keyvals))


def classname(*args: (CnArg | Iterable[CnArg]), sep=" ") -> Safe:
    """
    Another take on a classic `classnames`.
    The supplied arguments may be `str` | `bool` | `None` or iterables of such values.
    All `str` classes are flattened and joined into the single (unquoted!) string suitable
    for inclusion into the `class` attribute.
    """
    toks: list[str] = []
    append = toks.append
    esc = _html_escape
    isinst = isinstance
    safe = Safe
    _str = str

    for arg in args:
        if not arg or arg is True:
            pass
        elif isinst(arg, safe):
            append(arg)
        elif isinst(arg, _str):
            append(esc(arg))
        else:  # must be iterable
            try:
                for sub in arg:
                    if not arg or arg is True:
                        pass
                    elif isinst(sub, safe):
                        append(sub)
                    elif isinst(sub, _str):
                        append(esc(sub))
            except TypeError:
                pass

    return safe(sep.join([name for tok in toks if (name := tok.strip())]))


def style(s: str) -> Safe:
    """
    Wrapper for styles intended to be included into the `style` attribute.
    HTML-escapes the string. Triggers the CSS-syntax highlight.
    """
    return escape(s)


def handler(s: str) -> Safe:
    """
    Wrapper for inline javascript event handlers (`onlick` etc).
    HTML-escapes the string. Triggers the JS-syntax highlight.
    """
    return escape(s)


# is it really safe ?
def stylesheet(s: str) -> Safe:
    """
    Wrapper for inline css stylesheet for inclusion into the <style> tag.
    Doing almost nothing.
    Triggers the CSS-syntax highlight.
    """
    return Safe(s.replace("</style>", r"<\/style>"))


def script(s: str) -> Safe:
    """
    Wrapper for inline javascript for inclusion into the <script> tag.
    Escapes '</' according to the https://www.w3.org/TR/html401/appendix/notes.html#h-B.3.2
    Triggers the JS-syntax highlight.
    """
    return Safe(s.replace("</", r"<\/"))


def json_attr(val: Mapping[str, Any]) -> Safe:
    """
    JSON-format the attribute and HTML-escape it.
    """
    return Safe(_html_escape(_json.dumps(val, separators=(",", ":"))))


def csv_attr(*args: (CnArg | Iterable[CnArg])) -> Safe:
    """
    Same as the `classname` but joins string with commas instead of the whitespaces.
    """
    return classname(*args, sep=",")


# aliases
c = classname
document = markup
m = markup
t = text
