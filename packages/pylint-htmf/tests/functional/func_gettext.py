import htmf as ht

ht.m(f"<div>{ _('safe') }</div>")
ht.m(f"<div>{ gettext('safe') }</div>")
ht.m(f"<div>{ pgettext('ctx', 'safe') }</div>")

ht.m(f"<div>{ _('<unsafe>') }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div>{ gettext('&unsafe') }</div>")  # [htmf-unsafe-fexpression]
ht.m(f"<div>{ pgettext('ctx', '&unsafe') }</div>")  # [htmf-unsafe-fexpression]

# TODO: make it working
# ht.m(f"<div>{ gt_call }</div>")