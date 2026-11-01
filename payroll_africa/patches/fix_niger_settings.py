import frappe
from frappe.utils import flt


def execute():
	"""Niger Payroll Settings: correct CNSS/AMO rates and PIT threshold to 2025 CNSS/DGI values.

	Wrong defaults shipped in DocType JSON:
	  cnss_employee_rate: 3.6      → 5.25
	  cnss_ceiling      : 500,000  → 320,000 (8 × SMIG 40,000)
	  amo_employee_rate : 5.0      → 2.5
	  amo_employer_rate : 5.0      → 4.5
	  pit_threshold     : 0        → 25,000/month
	"""
	if not frappe.db.exists("DocType", "Niger Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Niger Payroll Settings", "cnss_employee_rate"))
	if abs(val - 3.6) < 0.01:
		corrections["cnss_employee_rate"] = 5.25

	val = flt(frappe.db.get_single_value("Niger Payroll Settings", "cnss_ceiling"))
	if abs(val - 500000) < 1:
		corrections["cnss_ceiling"] = 320000

	val = flt(frappe.db.get_single_value("Niger Payroll Settings", "amo_employee_rate"))
	if abs(val - 5.0) < 0.01:
		corrections["amo_employee_rate"] = 2.5

	val = flt(frappe.db.get_single_value("Niger Payroll Settings", "amo_employer_rate"))
	if abs(val - 5.0) < 0.01:
		corrections["amo_employer_rate"] = 4.5

	val = flt(frappe.db.get_single_value("Niger Payroll Settings", "pit_threshold"))
	if abs(val - 0) < 1 and val is not None:
		corrections["pit_threshold"] = 25000

	if corrections:
		frappe.db.set_single_value("Niger Payroll Settings", corrections)
