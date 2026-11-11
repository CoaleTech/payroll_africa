import frappe
from frappe.utils import flt


def execute():
	"""Burkina Faso Payroll Settings: correct CNSS/AMO rates to 2025/2026 statutory values.

	Wrong defaults shipped in DocType JSON:
	  cnss_employee_rate: 5.5    → 8.0    (CNSS employee rate)
	  cnss_employer_rate: 16.0   → 17.5   (CNSS employer rate)
	  cnss_ceiling      : 540,000 → 800,000
	  minimum_wage      : 65,000  → 45,000  (SMIG Burkina Faso)
	  amo_employer_rate : 4.0    → 2.5    (AMO employer matches employee)
	  pit_threshold     : 0      → 30,000/month (IUTS exemption)
	"""
	if not frappe.db.exists("DocType", "Burkina Faso Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Burkina Faso Payroll Settings", "cnss_employee_rate"))
	if abs(val - 5.5) < 0.01:
		corrections["cnss_employee_rate"] = 8.0

	val = flt(frappe.db.get_single_value("Burkina Faso Payroll Settings", "cnss_employer_rate"))
	if abs(val - 16.0) < 0.01:
		corrections["cnss_employer_rate"] = 17.5

	val = flt(frappe.db.get_single_value("Burkina Faso Payroll Settings", "cnss_ceiling"))
	if abs(val - 540000) < 1:
		corrections["cnss_ceiling"] = 800000

	val = flt(frappe.db.get_single_value("Burkina Faso Payroll Settings", "minimum_wage"))
	if abs(val - 65000) < 1:
		corrections["minimum_wage"] = 45000

	val = flt(frappe.db.get_single_value("Burkina Faso Payroll Settings", "amo_employer_rate"))
	if abs(val - 4.0) < 0.01:
		corrections["amo_employer_rate"] = 2.5

	val = flt(frappe.db.get_single_value("Burkina Faso Payroll Settings", "pit_threshold"))
	if abs(val - 0) < 1 and val is not None:
		corrections["pit_threshold"] = 30000

	if corrections:
		frappe.db.set_single_value("Burkina Faso Payroll Settings", corrections)
