import frappe

# BURS resident individual PAYE (PwC Worldwide Tax Summaries, reviewed Jan 2026).
CORRECT = [
	(0, 48000, 0),
	(48001, 84000, 5),
	(84001, 120000, 12.5),
	(120001, 156000, 18.75),
	(156001, 0, 25),
]

# Values earlier releases / installs wrote: top-rate 26.5%, or 48,000-wide brackets.
WRONG = [
	[(0, 48000, 0), (48001, 84000, 5), (84001, 120000, 12.5), (120001, 156000, 18.75), (156001, 192000, 25), (192001, 0, 26.5)],
	[(0, 48000, 0), (48001, 96000, 5), (96001, 144000, 12.5), (144001, 192000, 18.75), (192001, 240000, 25), (240001, 0, 26.5)],
]


def _fix(child_doctype, parent, rate_field):
	rows = frappe.get_all(
		child_doctype,
		filters={"parent": parent},
		fields=["name", "from_amount", "to_amount", rate_field],
		order_by="idx",
	)
	current = [(float(r.from_amount or 0), float(r.to_amount or 0), float(r[rate_field] or 0)) for r in rows]
	if current not in WRONG:
		return  # already correct or edited by the user: leave untouched
	for r in rows[len(CORRECT):]:
		frappe.db.delete(child_doctype, {"name": r.name})
	for r, (frm, to, rate) in zip(rows, CORRECT):
		frappe.db.set_value(
			child_doctype, r.name, {"from_amount": frm, "to_amount": to, rate_field: rate}
		)


def execute():
	"""Botswana PAYE: fix top rate (25%) and bracket widths in settings and the HRMS slab."""
	if frappe.db.exists("DocType", "Botswana PAYE Band"):
		_fix("Botswana PAYE Band", "Botswana Payroll Settings", "rate")
	if frappe.db.exists("Income Tax Slab", "Botswana PAYE 2025"):
		_fix("Taxable Salary Slab", "Botswana PAYE 2025", "percent_deduction")
