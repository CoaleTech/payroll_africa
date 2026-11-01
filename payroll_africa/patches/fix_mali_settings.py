import frappe
from frappe.utils import flt


def execute():
	"""Mali Payroll Settings: correct INSS/AMO rates and PIT threshold to 2025 INPS/DGI values.

	Wrong defaults shipped in DocType JSON (setup before this patch):
	  inss_employer_rate: 8.4  → 5.4
	  amo_employee_rate : 3.0  → 2.0
	  amo_employer_rate : 4.0  → 3.5
	  pit_threshold     : 650,000 (annual) → 175,000 (monthly barème threshold)
	"""
	if not frappe.db.exists("DocType", "Mali Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Mali Payroll Settings", "inss_employer_rate"))
	if abs(val - 8.4) < 0.01:
		corrections["inss_employer_rate"] = 5.4

	val = flt(frappe.db.get_single_value("Mali Payroll Settings", "amo_employee_rate"))
	if abs(val - 3.0) < 0.01:
		corrections["amo_employee_rate"] = 2.0

	val = flt(frappe.db.get_single_value("Mali Payroll Settings", "amo_employer_rate"))
	if abs(val - 4.0) < 0.01:
		corrections["amo_employer_rate"] = 3.5

	val = flt(frappe.db.get_single_value("Mali Payroll Settings", "pit_threshold"))
	if abs(val - 650000) < 1:
		corrections["pit_threshold"] = 175000

	if corrections:
		frappe.db.set_single_value("Mali Payroll Settings", corrections)
