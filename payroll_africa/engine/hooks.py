import frappe
from frappe.utils import flt

from payroll_africa.engine.registry import get_calculator


def on_salary_slip_validate(doc, method):
	"""Hook into Salary Slip validate to compute statutory deductions."""
	country = get_employee_country(doc.employee, doc.company)
	if not country:
		return

	# Check if Payroll Africa is enabled globally
	settings = frappe.get_cached_doc("Payroll Africa Settings")
	if not settings.enabled:
		return

	# Check if this specific country is enabled
	from payroll_africa.boot import COUNTRY_FIELD_MAP
	field = COUNTRY_FIELD_MAP.get(country)
	if field and not settings.get(field):
		frappe.throw(
			frappe._("Payroll for {0} is disabled in Payroll Africa Settings").format(country),
			title=frappe._("Country Disabled"),
		)

	calculator = get_calculator(country)
	if not calculator:
		return

	results = calculator.compute(doc)

	for component_name, data in results.items():
		_set_component_amount(doc, component_name, data["amount"], data["is_employer_only"])

	# Recalculate net pay after overriding deduction amounts
	doc.set_net_pay()


def get_employee_country(employee, company):
	"""Get payroll country from Employee, falling back to Company country."""
	country = frappe.db.get_value("Employee", employee, "payroll_country")
	if not country:
		country = frappe.db.get_value("Company", company, "country")
	return country


def _set_component_amount(doc, component_name, amount, is_employer_only):
	"""Set amount on an existing deduction row, or append if missing."""
	for row in doc.deductions:
		if row.salary_component == component_name:
			precision = row.precision("amount") if hasattr(row, "precision") else None
			row.amount = flt(amount, precision)
			row.default_amount = row.amount
			return

	# Component not in salary structure - append it
	component_doc = frappe.get_cached_doc("Salary Component", component_name)
	doc.append("deductions", {
		"salary_component": component_name,
		"abbr": component_doc.salary_component_abbr,
		"amount": flt(amount),
		"default_amount": flt(amount),
		"do_not_include_in_total": 1 if is_employer_only else 0,
		"statistical_component": 1 if is_employer_only else 0,
		"exempted_from_income_tax": component_doc.exempted_from_income_tax or 0,
	})
