import frappe

from payroll_africa.engine.utils import get_effective_ssa_values


def get_employee_country(employee, company, salary_structure=None, on_date=None):
	"""Resolve payroll country for an employee.

	Preference order:
	1. ``Salary Structure Assignment.payroll_country`` for the active assignment.
	2. ``Employee.payroll_country``.
	3. ``Company.country``.
	"""
	if salary_structure and on_date:
		ssa = get_effective_ssa_values(
			employee,
			company,
			salary_structure,
			on_date,
			["payroll_country"],
		)
		if ssa.get("payroll_country"):
			return ssa.get("payroll_country")

	country = frappe.db.get_value("Employee", employee, "payroll_country")
	if not country:
		country = frappe.db.get_value("Company", company, "country")
	return country
