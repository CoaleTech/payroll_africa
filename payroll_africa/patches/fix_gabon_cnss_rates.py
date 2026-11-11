import frappe
from frappe.utils import flt


def execute():
	"""Gabon Payroll Settings: correct CNSS employee and employer rates for 2026 reform.

	Post-reform 2026 rates (PwC):
	  cnss_employee_rate: 2.5  → 5    (only if use_2026_reform is on)
	  cnss_employer_rate: 20.1 → 18   (only if use_2026_reform is on)

	Only corrects values still at the known-wrong defaults and only when the 2026 reform
	flag is enabled; never clobbers user edits.
	"""
	if not frappe.db.exists("DocType", "Gabon Payroll Settings"):
		return

	use_reform = flt(frappe.db.get_single_value("Gabon Payroll Settings", "use_2026_reform"))
	if not use_reform:
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Gabon Payroll Settings", "cnss_employee_rate"))
	if abs(val - 2.5) < 0.01:
		corrections["cnss_employee_rate"] = 5

	val = flt(frappe.db.get_single_value("Gabon Payroll Settings", "cnss_employer_rate"))
	if abs(val - 20.1) < 0.01:
		corrections["cnss_employer_rate"] = 18

	if corrections:
		frappe.db.set_single_value("Gabon Payroll Settings", corrections)
