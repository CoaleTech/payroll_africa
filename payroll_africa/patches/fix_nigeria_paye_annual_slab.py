import frappe

from payroll_africa.setup import NIGERIA_PAYE_SLAB_BANDS


def execute():
	"""Nigeria PAYE 2025: replace monthly (FIRS/12) bands with correct annual FIRS bands (PITA s.33).

	Guard: only runs when the first slab row still has to_amount == 25,000 (the old monthly value).
	"""
	if not frappe.db.exists("Income Tax Slab", "Nigeria PAYE 2025"):
		return

	rows = frappe.get_all(
		"Taxable Salary Slab",
		filters={"parent": "Nigeria PAYE 2025"},
		order_by="idx",
		fields=["name", "to_amount"],
	)
	if not rows:
		return

	# Guard: first band must still be at the wrong monthly ceiling of 25,000.
	if rows[0]["to_amount"] != 25000:
		return

	if len(rows) != len(NIGERIA_PAYE_SLAB_BANDS):
		return

	for row, band in zip(rows, NIGERIA_PAYE_SLAB_BANDS):
		frappe.db.set_value(
			"Taxable Salary Slab",
			row["name"],
			{
				"from_amount": band["from_amount"],
				"to_amount": band["to_amount"],
				"percent_deduction": band["rate"],
			},
		)
