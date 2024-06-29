from __future__ import annotations

import typing as t

import json
from html import escape as _html_escape
from urllib.parse import quote as _urllib_quote

Arg = str | bool | None | int | float
Attrs = t.Mapping[str, Arg]
CnArg = str | bool | None


def _format_tok(tok: str | int | float) -> Safe:
    return escape(tok if isinstance(tok, str) else f"{ tok }")


def _format_kv(args: Attrs) -> Safe:
    keyvals: list[str] = []

    for k, v in sorted(args.items()):
        if v is None or v is False:
            pass
        elif not k:  # special catch for the empty key
            pass
        elif v is True:  # boolean attribute e.g. 'hidden', 'disabled'
            keyvals.append(escape(k))
        else:  # kv attribute
            keyvals.append(f'{ escape(k) }="{ _format_tok(v) }"')

    return Safe(" ".join(keyvals))


def _join_truthy_strings(*args: (CnArg | t.Iterable[CnArg]), sep: str) -> Safe:
    toks: list[str] = []

    for arg in args:
        if arg is None or arg is True or arg is False:
            pass
        elif isinstance(arg, str):
            toks.append(arg)
        else:
            toks.extend(f for f in arg if isinstance(f, str))

    return escape(sep.join([name for tok in toks if (name := tok.strip())]))


class Safe(str):
    """
    Noop class for marking the string as HTML-safe.
    Used for marking strings safe and preventing double escape at runtime.
    Used for type annotations.

    Not intended to be instantiated outside of the library code !
    """

    pass


def safe(s: Safe) -> Safe:
    """
    noop wrapper for HTML-safe strings.
    Useful for linting if linter fails to infer to corrent type
    """
    return s


def dangerously_mark_as_safe(s: str) -> Safe:
    """
    Mark the string as safe, promoting it to the Safe class.
    Escape hatch if you really need to include some not-to-be esscaped string.
    """
    return Safe(s)


def escape(s: str | None) -> Safe:
    """HTML-escape the string making it safe for inclusion in the markup"""
    if isinstance(s, Safe):
        return s
    if s:
        return Safe(_html_escape(s))
    return Safe("")


def url(string: str, /, safe="/", errors: str | None = None) -> Safe:
    """Make the string url-safe and escape HTML-unsafe characters"""
    return escape(_urllib_quote(string, safe=safe, errors=errors))


def markup(s: str | None | bool) -> Safe:
    """
    Strips the whitespaces and marks the string as safe.
    Triggers the HTML-syntax highlight
    """
    return Safe(s.strip() if isinstance(s, str) else "")


def text(*args: Arg | t.Iterable[Arg]) -> Safe:
    """
    Basic building block for HTML texts and fragments.

    The arguments may be `None` | `str` | `bool` | `int` | `float` or iterables of such types.
    Supplied values are flattened into the one single list.
    Nones and bools are dropped as in JSX. Numbers are stringified.
    Strings are escaped unless marked as safe.

    Returns the single string of values joined.
    """
    texts: list[str] = []

    for arg in args:
        if arg is None or arg is True or arg is False:
            pass
        elif isinstance(arg, (str, int, float)):
            texts.append(_format_tok(arg))
        else:  # iterable for sure
            texts.extend(
                _format_tok(subarg) for subarg in arg if not (subarg is None or subarg is True or subarg is False)
            )

    return Safe("".join(text for text in texts if text))


def attr(arg: Attrs | None = None, /, **kwargs: Arg) -> Safe:
    """
    Accepts the dictionary of name-value pairs and/or name-value keywords.
    Keywords override the dictionary.
    Formats the result as the quoted HTML-attributes suitable for direct inclusion into the tags.
    [EXAMPLE HERE]
    - `True` values are rendered as just the name, e.g `hidden`
    - `False` values are discarded
    - string values are rendered as name-value pairs, e.g. `type = "checkbox"`
    - number values are interpolated, e.g. `tabindex="-1"`

    Return the single string of whitespace-separated pairs.
    """
    return _format_kv((arg | kwargs) if arg else kwargs)


def classname(*args: (CnArg | t.Iterable[CnArg])) -> Safe:
    """
    Another take on a classic `classnames`.
    The supplied arguments may be `str` | `bool` | `None` or iterables of such values.
    All `str` classes are flattened and joined into the single (unquoted!) string suitable
    for inclusion into the `class` attribute.
    [EXAMPLE HERE]
    """
    return _join_truthy_strings(*args, sep=" ")


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
    Doing almost nothing.
    Triggers the JS-syntax highlight.
    """
    return Safe(s.replace("</script>", r"<\/script>"))


def json_attr(val: t.Mapping[str, t.Any]) -> Safe:
    """
    JSON-format the attribute and HTML-escape it.
    Useful for htmx hx-vals attribute
    """
    return escape(json.dumps(val, separators=(",", ":")))


def csv_attr(*args: (CnArg | t.Iterable[CnArg])) -> Safe:
    """
    Same as the `classnames` but joins string with commas instead of the whitespaces.
    Useful for htmx hx-trigger attribute
    """
    return _join_truthy_strings(*args, sep=",")
