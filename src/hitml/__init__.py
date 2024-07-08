"""hitml: Python f-strings HTML templating library"""

# Licenced under the MIT License: https://www.opensource.org/licenses/mit-license.php

__version__ = "0.1.0.dev1"

from .hitml import (
    attr,
    Attrs,
    classname,
    csv_attr,
    dangerously_mark_as_safe,
    handler,
    json_attr,
    markup,
    safe,
    Safe,
    SafeOf,
    script,
    style,
    stylesheet,
    text,
    # aliases
    classname as c,
    markup as document,
    markup as m,
    text as t,
)

__all__ = [
    "attr",
    "Attrs",
    "c",
    "classname",
    "csv_attr",
    "dangerously_mark_as_safe",
    "document",
    "handler",
    "json_attr",
    "m",
    "markup",
    "safe",
    "Safe",
    "SafeOf",
    "script",
    "style",
    "stylesheet",
    "t",
    "text",
]
