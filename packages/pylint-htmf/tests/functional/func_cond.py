import htmf as ht
from htmf import Safe

# ternary
ht.m(f"<div> { 'a' if foo() else 'b' } </div>")

ht.m(f"<div> { 'a' if foo() else None } </div>")  # [htmf-unsafe-fexpression]

ht.m(f"<div> { 'a' if foo() else 'a' if bar() else 'c' } </div>")

safe_lit = "a"
unsafe_lit = "<a"
annotated: Safe
safe_int = 42

def Widget() -> Safe:
    return ht.m(f"<div></div>")


def WidgetMaybe() -> Safe | None:
    return ht.m(f"<div></div>")


rc = Widget()


ht.m(f"<div> { safe_lit if foo() else safe_lit } </div>")
ht.m(f"<div> { safe_lit if foo() else unsafe_lit } </div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div> { Widget() if foo() else ht.t() if bar() else annotated if foo() else rc} </div>")

ht.m(f"<div> { safe_lit if foo() else safe_int } </div>")


def Widget2(arg: Safe):
    ht.m(f"<div> { Widget() if foo() else ht.t() if bar() else arg } </div>")


# ors

ht.m(f"<div>{ 'a' or 'b' }</div>")
ht.m(f"<div>{ 'a' or None }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div>{ Widget() or rc }</div>")
ht.m(f"<div>{ Widget() or 'a' or '?' }</div>")
ht.m(f"<div>{ None or Widget() or 'a' or '?' }</div>")
ht.m(f"<div>{ WidgetMaybe() or Widget() }</div>")
ht.m(f"<div>{ Widget() or WidgetMaybe() }</div>")  # [htmf-unsafe-fexpression]

ht.m(f"<div>{ 0 or 1 or None or 3.5 or 'wtf' }</div>")