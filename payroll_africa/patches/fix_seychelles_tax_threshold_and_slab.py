import frappe

# SRC citizen rates (src.gov.sc, rates from 1 June 2018). Monthly bands for the
# calculator's settings table; the HRMS slab holds the same bands x 12 because HRMS
# annualises monthly salary before slab lookup.
_MONTHLY = [(0, 8555.50, 0), (8555.50, 10000, 15), (10000, 83333, 20), (83333, 0, 30)]
_ANNUAL = [(0, 102666, 0), (102666, 120000, 15), (120000, 999996, 20), (999996, 0, 30)]

# Earlier releases wrote 10,027.75 / 13,630 as the 15% / 20% break points.
_OLD_MONTHLY = [(0, 8555.50, 0), (8555.50, 10027.75, 15), (10027.75, 13630, 20), (13630, 0, 30)]
_OLD_ANNUAL = [(0, 102666, 0), (102666, 120333, 15), (120333, 163560, 20), (163560, 0, 30)]

_SLAB_NAME = "Seychelles PAYE 2026"


def _rows(child_doctype, parent, rate_field):
	rows = frappe.get_all(
		child_doctype,
		filters={"parent": parent},
		fields=["name", "from_amount", "to_amount", rate_field],
		order_by="idx",
	)
	current = [(float(r.from_amount or 0), float(r.to_amount or 0), float(r[rate_field] or 0)) for r in rows]
	return rows, current


def _rewrite(child_doctype, parent, rate_field, old_variants, new):
	"""Replace known-wrong band tables only; a table the user edited is left alone."""
	rows, current = _rows(child_doctype, parent, rate_field)
	if current not in old_variants or len(rows) != len(new):
		return
	for r, (frm, to, rate) in zip(rows, new):
		frappe.db.set_value(child_doctype, r.name, {"from_amount": frm, "to_amount": to, rate_field: rate})


def execute():
	"""Seychelles: threshold 0 -> 8,555.50, and correct the PAYE bands (settings and slab)."""
	if frappe.db.exists("DocType", "Seychelles Payroll Settings"):
		if not float(frappe.db.get_single_value("Seychelles Payroll Settings", "tax_free_threshold") or 0):
			frappe.db.set_single_value("Seychelles Payroll Settings", "tax_free_threshold", 8555.5)
		_rewrite("Seychelles PAYE Band", "Seychelles Payroll Settings", "rate", [_OLD_MONTHLY], _MONTHLY)

	if frappe.db.exists("Income Tax Slab", _SLAB_NAME):
		# The slab was first created with monthly values (HRMS needs annual), then annualised
		# with the wrong break points; handle both.
		_rewrite("Taxable Salary Slab", _SLAB_NAME, "percent_deduction", [_OLD_MONTHLY, _OLD_ANNUAL], _ANNUAL)
