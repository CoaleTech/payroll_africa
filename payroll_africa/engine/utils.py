import frappe


def get_effective_ssa_values(
	employee: str,
	company: str,
	salary_structure: str,
	on_date,
	fields: list[str],
) -> "frappe._dict":
	"""Return the most recent submitted Salary Structure Assignment values.

	Mirrors the pattern used by india_payroll: pick the assignment matching the
	employee, company and salary structure whose ``from_date`` is on or before
	``on_date``, ordered by effective date descending.
	"""
	row = frappe.db.get_value(
		"Salary Structure Assignment",
		filters={
			"employee": employee,
			"company": company,
			"salary_structure": salary_structure,
			"from_date": ("<=", on_date),
			"docstatus": 1,
		},
		fieldname=fields,
		order_by="from_date desc",
		as_dict=True,
	)
	return row or frappe._dict()
