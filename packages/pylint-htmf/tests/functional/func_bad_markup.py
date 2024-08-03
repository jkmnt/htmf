import htmf as ht
import htmf

# basic broken markup
ht.m("</div><div>")  # [htmf-bad-markup]

# default wrappers
ht.markup("</div><div>")  # [htmf-bad-markup]
htmf.markup("</div><div>")  # [htmf-bad-markup]
htmf.m("</div><div>")  # [htmf-bad-markup]
htmf.document("</div><div>")  # [htmf-bad-markup]

# make sure regexps are ok and full-matching
ht.markup2("</div><div>")
ht.ma("</div><div>")

# good markup
ht.m("<div></div>")

# empty
ht.m("")  # [htmf-bad-markup]

# flat markup, should error
ht.m("<div></div></div></div>")  # [htmf-bad-markup]

# flat with scopes, ok
# htmf-scopes=div
ht.m("<div></div><div></div>")

# some broken attributes
ht.m("<div class= >")  # [htmf-bad-markup]

# tr w/o table
ht.m("<tr></tr>")  # [htmf-bad-markup]
# tr with table, ok
# htmf-scopes=table
ht.m("<tr></tr>")

# document - must have <html>
ht.document("<div></div>")  # [htmf-bad-markup]
# ok
ht.document("<!doctype html><html><div></div></html>")

# recognize multiline
# +2: [htmf-bad-markup]
ht.m(
    """
    <div>
        <div>
    </div>
"""
)

# recognize nested
ht.m(
    f"""
    <div>
        { ht.m(f'''
            <span>
                {
                    ht.m('<div>') # [htmf-bad-markup]
                }
            </span>
        ''')}
    </div>
"""
)

###############
# f-expressions

# basic broken markup
ht.m(f"</div><div>")  # [htmf-bad-markup]

# good markup
ht.m(f"<div></div>")

# empty
ht.m(f"")  # [htmf-bad-markup]

# flat markup, should error
ht.m(f"<div></div></div></div>")  # [htmf-bad-markup]

# flat with scopes, ok
# htmf-scopes=div
ht.m(f"<div></div><div></div>")

# some broken attributes
ht.m(f"<div class= >")  # [htmf-bad-markup]

# tr w/o table
ht.m(f"<tr></tr>")  # [htmf-bad-markup]
# tr with table, ok
# htmf-scopes=table
ht.m(f"<tr></tr>")

# document - must have <html>
ht.document(f"<div></div>")  # [htmf-bad-markup]
# ok
ht.document(f"<!doctype html><html><div></div></html>")

# recognize multiline
# +2: [htmf-bad-markup]
ht.m(
    f"""
    <div>
        <div>
    </div>
"""
)

# recognize nested
ht.m(f"""
    <div>
        { ht.m(f'''
            <span>
                {
                    ht.m(f'<div>') # [htmf-bad-markup]
                }
            </span>
        ''')}
    </div>
""")