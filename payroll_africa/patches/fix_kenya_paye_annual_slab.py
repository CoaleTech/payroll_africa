import frappe

from payroll_africa.setup import KENYA_PAYE_SLAB_BANDS


def execute():
	"""Kenya PAYE: slab bands must be annual (HRMS annualises), personal relief folded into a 0% band."""
	if not frappe.db.exists("Income Tax Slab", "Kenya PAYE 2025"):
		return

	rows = frappe.get_all(
		"Taxable Salary Slab",
		filters={"parent": "Kenya PAYE 2025"},
		order_by="idx",
		pluck="name",
	)
	if len(rows) != len(KENYA_PAYE_SLAB_BANDS):
		return

	for name, band in zip(rows, KENYA_PAYE_SLAB_BANDS, strict=True):
		frappe.db.set_value(
			"Taxable Salary Slab",
			name,
			{
				"from_amount": band["from_amount"],
				"to_amount": band["to_amount"],
				"percent_deduction": band["rate"],
			},
		)
	frappe.clear_document_cache("Income Tax Slab", "Kenya PAYE 2025")
