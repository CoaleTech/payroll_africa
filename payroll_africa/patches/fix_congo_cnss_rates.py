import frappe
from frappe.utils import flt


def execute():
	"""Congo Payroll Settings: correct CNSS employer rate, CNSS ceiling and CAMU rate.

	PwC 2025:
	  cnss_rate (employer): 21.5  → 20.285
	  cnss_ceiling        : 1,000,000 → 1,200,000
	  cnamgs_rate (CAMU)  : 4     → 0.5

	Only corrects values still at the known-wrong defaults; never clobbers user edits.
	"""
	if not frappe.db.exists("DocType", "Congo Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Congo Payroll Settings", "cnss_rate"))
	if abs(val - 21.5) < 0.01:
		corrections["cnss_rate"] = 20.285

	val = flt(frappe.db.get_single_value("Congo Payroll Settings", "cnss_ceiling"))
	if abs(val - 1000000) < 1:
		corrections["cnss_ceiling"] = 1200000

	val = flt(frappe.db.get_single_value("Congo Payroll Settings", "cnamgs_rate"))
	if abs(val - 4) < 0.01:
		corrections["cnamgs_rate"] = 0.5

	if corrections:
		frappe.db.set_single_value("Congo Payroll Settings", corrections)
