import htmf as ht
from htmf import Safe


# args
def Widget(header: Safe, body: Safe) -> Safe:
    return ht.m(f"<div>{ header } { body }</div>")


def Widget2(header: None):
    return ht.m(f"<div>{ header }</div>")  # [htmf-unsafe-fexpression]


def Widget3(header: int):
    return ht.m(f"<div>{ header }</div>")


def Widget4(header: Safe | None):
    return ht.m(f"<div>{ header }</div>")  # [htmf-unsafe-fexpression]


def Widget5(header: Safe | Safe):
    return ht.m(f"<div>{ header }</div>")

def Widget7(header: Safe | int | float):
    return ht.m(f"<div>{ header }</div>")

def Widget8() -> Safe | int:
    return Safe("")

# vars
safe_var: Safe
unsafe_var: str
safe_rc = Widget(ht.t(), ht.t())
unsafe_rc = Widget2(ht.t())
safe_int: int
safe_float: float
safe_int_or_float: int | float
safe_or_int_rc = Widget8()

bool_unsafe: bool

ht.m(f"<div>{ safe_var }</div>")

ht.m(f"<div>{ unsafe_var }</div>")  # [htmf-unsafe-fexpression]

ht.m(f"<div>{ safe_rc }</div>")
ht.m(f"<div>{ unsafe_rc }</div>") # [htmf-unsafe-fexpression]

ht.m(f"<div>{ safe_int }</div>")
ht.m(f"<div>{ safe_float }</div>")
ht.m(f"<div>{ safe_int_or_float }</div>")
ht.m(f"<div>{ safe_or_int_rc }</div>")

ht.m(f"<div>{ bool_unsafe }</div>") # [htmf-unsafe-fexpression]

# reannotated as unsafe
def Widget6(header: Safe):
    a: str = header
    return ht.m(f"<div>{ a } </div>") # [htmf-unsafe-fexpression]

def now() -> int:
    return 1

ht.m(f"<div>{ now() }</div>")