import time
import htmf as ht
from htmf import Safe

# imported with Safe rc. htmf's own functions
ht.m(
    f"""
    <div>
        { ht.m('<div></div>') }
        { ht.t() }
        { ht.attr() }
        { ht.c() }
        { ht.script('') }
        { ht.handler('') }
        { ht.json_attr({}) }
        { ht.csv_attr() }
        { ht.style('') }
        { ht.stylesheet('') }
        { ht.mark_as_safe('') }
    </div>
"""
)

# unsafe imported
ht.m(f"<div>{ ht.unescape('<div></div>') }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div>{ time.time() }</div>")  # [htmf-unsafe-fexpression]


# local component
def Widget() -> Safe:
    return ht.m(f"<div></div>")


def UnsafeWidget():
    return ""


def StillUnsafeWidget():
    return ht.mark_as_safe("")


def UnsafeWidget2() -> str:
    return ""


def UnsafeWidget3() -> str | None | Safe:
    return ""


# or-ed rc type
def SafeWidget2() -> Safe | Safe:
    return Safe("")


ht.m(f"<div>{ Widget() }</div>")
ht.m(f"<div>{ SafeWidget2() }</div>")

ht.m(f"<div>{ UnsafeWidget() }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div>{ StillUnsafeWidget() }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div>{ UnsafeWidget2() }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div>{ UnsafeWidget3() }</div>")  # [htmf-unsafe-fexpression]
