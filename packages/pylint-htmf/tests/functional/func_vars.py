import time
import htmf as ht
from htmf import Safe


# args
def Widget(header: Safe, body: Safe) -> Safe:
    return ht.m(f"<div>{ header } { body }</div>")


def Widget2(header: None):
    return ht.m(f"<div>{ header }</div>")  # [htmf-unsafe-fexpression]


def Widget3(header: int):
    return ht.m(f"<div>{ header }</div>")  # [htmf-unsafe-fexpression]


def Widget4(header: Safe | None):
    return ht.m(f"<div>{ header }</div>")  # [htmf-unsafe-fexpression]


def Widget5(header: Safe | Safe):
    return ht.m(f"<div>{ header }</div>")


# vars
safe_var: Safe
unsafe_var: str
safe_rc = Widget(ht.t(), ht.t())
unsafe_rc = Widget2(ht.t())

ht.m(f"<div>{ safe_var }</div>")

ht.m(f"<div>{ unsafe_var }</div>")  # [htmf-unsafe-fexpression]

ht.m(f"<div>{ safe_rc }</div>")
ht.m(f"<div>{ unsafe_rc }</div>") # [htmf-unsafe-fexpression]

# reannotated as unsafe
def Widget6(header: Safe):
    a: str = header
    return ht.m(f"<div>{ a } </div>") # [htmf-unsafe-fexpression]