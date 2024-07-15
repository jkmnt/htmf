"""htmf: Python f-strings HTML templating library"""

# Licenced under the MIT License: https://www.opensource.org/licenses/mit-license.php

__version__ = "0.2.0.dev1"

from .htmf import (
    attr,
    Attrs,
    classname,
    csv_attr,
    handler,
    json_attr,
    mark_as_safe,
    markup,
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
