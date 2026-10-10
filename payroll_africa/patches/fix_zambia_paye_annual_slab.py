import frappe

from payroll_africa.setup import ZAMBIA_PAYE_SLAB_BANDS


def execute():
	"""Zambia PAYE: slab bands must be annual (HRMS annualises) and NAPSA is not tax-exempt."""
	if frappe.db.exists("Income Tax Slab", "Zambia PAYE 2025"):
		rows = frappe.get_all(
			"Taxable Salary Slab",
			filters={"parent": "Zambia PAYE 2025"},
			order_by="idx",
			pluck="name",
		)
		if len(rows) == len(ZAMBIA_PAYE_SLAB_BANDS):
			for name, band in zip(rows, ZAMBIA_PAYE_SLAB_BANDS):
				frappe.db.set_value(
					"Taxable Salary Slab",
					name,
					{
						"from_amount": band["from_amount"],
						"to_amount": band["to_amount"],
						"percent_deduction": band["rate"],
					},
				)

	if frappe.db.exists("Salary Component", "NAPSA Employee ZM"):
		frappe.db.set_value("Salary Component", "NAPSA Employee ZM", "exempted_from_income_tax", 0)
		# Structure rows copy the flag from the component when saved; clear stale copies.
		frappe.db.set_value(
			"Salary Detail",
			{"salary_component": "NAPSA Employee ZM", "parenttype": "Salary Structure"},
			"exempted_from_income_tax",
			0,
		)
