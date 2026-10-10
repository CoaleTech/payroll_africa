import frappe
from frappe.utils import flt


def standard_slip_conditions(filters):
	"""Build standard WHERE conditions for Salary Slip reports."""
	conditions = ""
	if filters.get("company"):
		conditions += " AND ss.company = %(company)s"
	if filters.get("from_date"):
		conditions += " AND ss.start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND ss.end_date <= %(to_date)s"
	return conditions


def fetch_component_amounts(slip_names, components, parentfield=("deductions", "employer_contributions")):
	"""Batch-fetch Salary Detail amounts for salary slips and components.
	`parentfield` is one table name or a tuple (employer components live in employer_contributions).
	Returns: {slip_name: {component_name: amount}}
	"""
	if not slip_names or not components:
		return {}

	rows = frappe.db.sql(
		"""
		SELECT parent, salary_component, amount
		FROM `tabSalary Detail`
		WHERE parent IN %s
			AND salary_component IN %s
			AND parentfield IN %s
		""",
		(slip_names, components, (parentfield,) if isinstance(parentfield, str) else tuple(parentfield)),
		as_dict=True,
	)

	result = {}
	for row in rows:
		result.setdefault(row.parent, {})[row.salary_component] = flt(row.amount)
	return result
