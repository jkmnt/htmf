import htmf as ht

ht.m(f"<div>{ 'safe' }</div>")

ht.m(f"<div>{ '<unsafe>' }</div>")  # [htmf-unsafe-fexpression]

ht.m(f"<div>{ '&unsafe' }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"""<div>{ '"unsafe' }</div>""")  # [htmf-unsafe-fexpression]
ht.m(f"""<div>{ "unsafe'" }</div>""")  # [htmf-unsafe-fexpression]

# literal defined here

safe_lit = "safe"

ht.m(f"<div>{ safe_lit }</div>")

# safe literal with branches
if bla():
    safe_lit2 = "safe"
else:
    safe_lit2 = "safe_too"

ht.m(f"<div>{ safe_lit2 }</div>")


# maybesafe literal with branches
if bla():
    safe_lit3 = "safe"
else:
    safe_lit3 = None

ht.m(f"<div>{ safe_lit3 }</div>")  # [htmf-unsafe-fexpression]

ht.m(f"<div>{ 1 }</div>")
ht.m(f"<div>{ 1.0 }</div>")
