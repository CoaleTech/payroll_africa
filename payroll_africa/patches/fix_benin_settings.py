import frappe
from frappe.utils import flt


def execute():
	"""Benin Payroll Settings: correct AMO rates, CNSS ceiling, and PIT threshold.

	Wrong defaults shipped in DocType JSON:
	  amo_employee_rate: 3.5     → 0       (AMO not applicable; rate configurable if needed)
	  amo_employer_rate: 3.5     → 0       (same)
	  cnss_ceiling     : 500,000 → 0       (0 = uncapped per CNSS Bénin rules)
	  pit_threshold    : 0       → 60,000/month (IRPP exemption threshold)
	"""
	if not frappe.db.exists("DocType", "Benin Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Benin Payroll Settings", "amo_employee_rate"))
	if abs(val - 3.5) < 0.01:
		corrections["amo_employee_rate"] = 0

	val = flt(frappe.db.get_single_value("Benin Payroll Settings", "amo_employer_rate"))
	if abs(val - 3.5) < 0.01:
		corrections["amo_employer_rate"] = 0

	val = flt(frappe.db.get_single_value("Benin Payroll Settings", "cnss_ceiling"))
	if abs(val - 500000) < 1:
		corrections["cnss_ceiling"] = 0

	val = flt(frappe.db.get_single_value("Benin Payroll Settings", "pit_threshold"))
	if abs(val - 0) < 1 and val is not None:
		corrections["pit_threshold"] = 60000

	if corrections:
		frappe.db.set_single_value("Benin Payroll Settings", corrections)
