import frappe

from payroll_africa.setup import (
	KENYA_PAYE_ANNUAL_BANDS,
	UGANDA_PAYE_ANNUAL_BANDS,
	TANZANIA_PAYE_ANNUAL_BANDS,
	RWANDA_PAYE_ANNUAL_BANDS,
	BURUNDI_PAYE_ANNUAL_BANDS,
)


def _fix_slab(slab_name, annual_bands, wrong_first_to_amount):
	"""Replace monthly slab bands with correct annual bands.

	Guard: only corrects when the first band's to_amount equals the known-wrong
	monthly ceiling, preventing accidental re-run on already-correct slabs.
	"""
	if not frappe.db.exists("Income Tax Slab", slab_name):
		return

	rows = frappe.get_all(
		"Taxable Salary Slab",
		filters={"parent": slab_name},
		order_by="idx",
		fields=["name", "to_amount"],
	)
	if not rows:
		return

	if rows[0]["to_amount"] != wrong_first_to_amount:
		return

	if len(rows) != len(annual_bands):
		return

	for row, band in zip(rows, annual_bands):
		frappe.db.set_value(
			"Taxable Salary Slab",
			row["name"],
			{
				"from_amount": band["from_amount"],
				"to_amount": band["to_amount"],
				"percent_deduction": band["rate"],
			},
		)


def execute():
	"""East Africa PAYE 2025: replace per-month slab bands with annual bands (monthly × 12).

	HRMS annualises monthly taxable income before applying the slab.  The old
	setup wrote the monthly KRA/URA/TRA/RRA/OBR bands directly; this patch
	updates each slab to the correct annual equivalents.

	Guards on each country's known-wrong first-band to_amount so re-runs are safe.
	"""
	_fix_slab("Kenya PAYE 2025",    KENYA_PAYE_ANNUAL_BANDS,    wrong_first_to_amount=24000)
	_fix_slab("Uganda PAYE 2025",   UGANDA_PAYE_ANNUAL_BANDS,   wrong_first_to_amount=235000)
	_fix_slab("Tanzania PAYE 2025", TANZANIA_PAYE_ANNUAL_BANDS, wrong_first_to_amount=270000)
	_fix_slab("Rwanda PAYE 2025",   RWANDA_PAYE_ANNUAL_BANDS,   wrong_first_to_amount=60000)
	_fix_slab("Burundi PAYE 2025",  BURUNDI_PAYE_ANNUAL_BANDS,  wrong_first_to_amount=150000)
