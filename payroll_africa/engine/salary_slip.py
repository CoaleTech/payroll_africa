import frappe
from frappe.utils import flt

from payroll_africa.engine.hooks import get_employee_country
from payroll_africa.engine.registry import get_calculator


def apply_regional_deductions(doc):
	"""Regional hook for Salary Slip statutory African deductions.

	This is the target of the HRMS ``apply_regional_deductions`` regional
	override.  It replaces the previous ``doc_events`` ``validate`` hook.
	"""
	country = get_employee_country(
		doc.employee,
		doc.company,
		salary_structure=doc.salary_structure,
		on_date=doc.start_date,
	)
	if not country:
		return

	if not _is_country_enabled(country):
		return

	calculator = get_calculator(country)
	if not calculator:
		return

	results = calculator.compute(doc)
	for component_name, data in results.items():
		_set_component_amount(
			doc,
			component_name,
			data["amount"],
			data.get("is_employer_only", False),
		)


def _is_country_enabled(country):
	"""Check global Payroll Africa Settings and per-country enable flag."""
	if not frappe.db.exists("Payroll Africa Settings"):
		return False

	settings = frappe.get_cached_doc("Payroll Africa Settings")
	if not settings.enabled:
		return False

	from payroll_africa.boot import COUNTRY_FIELD_MAP

	field = COUNTRY_FIELD_MAP.get(country)
	if field and not settings.get(field):
		return False

	return True


def _get_employer_contributions_field():
	"""Return the Salary Slip child-table field used for employer contributions.

	HRMS exposes ``employer_contributions`` on ``Salary Structure`` and
	``Salary Structure Assignment``.  If the local Salary Slip DocType also has
	a child table for employer contributions, return its fieldname; otherwise
	return ``None`` and employer-only components fall back to ``deductions``
	with statistical flags for backward compatibility.
	"""
	meta = frappe.get_meta("Salary Slip")
	for field in meta.get_table_fields():
		if field.fieldname == "employer_contributions":
			return "employer_contributions"

	for field in meta.get_table_fields():
		if field.options == "Salary Detail" and (
			"employer" in field.fieldname.lower() or "contribution" in field.fieldname.lower()
		):
			return field.fieldname

	return None


def _set_component_amount(doc, component_name, amount, is_employer_only=False):
	"""Set amount on an existing row, or append if missing.

	Employer-only components are routed to the Salary Slip's
	``employer_contributions`` child table when it exists; otherwise they are
	kept in ``deductions`` with ``statistical_component`` /
	``do_not_include_in_total`` so they do not affect net pay.
	"""
	table_field = _get_employer_contributions_field() if is_employer_only else None
	target_table = table_field or "deductions"

	for row in doc.get(target_table) or []:
		if row.salary_component == component_name:
			precision = row.precision("amount") if hasattr(row, "precision") else None
			row.amount = flt(amount, precision)
			row.default_amount = row.amount
			return

	if not frappe.db.exists("Salary Component", component_name):
		frappe.log_error(
			title="Payroll Africa: Missing Salary Component",
			message=f"Salary Component '{component_name}' not found. Run Setup Wizard or bench migrate.",
		)
		return

	component_doc = frappe.get_cached_doc("Salary Component", component_name)
	row_data = {
		"salary_component": component_name,
		"abbr": component_doc.salary_component_abbr,
		"amount": flt(amount),
		"default_amount": flt(amount),
		"exempted_from_income_tax": component_doc.exempted_from_income_tax or 0,
	}

	if not table_field:
		row_data["do_not_include_in_total"] = 1 if is_employer_only else 0
		row_data["statistical_component"] = 1 if is_employer_only else 0

	doc.append(target_table, row_data)
