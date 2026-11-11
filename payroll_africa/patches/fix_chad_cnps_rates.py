import frappe
from frappe.utils import flt


def execute():
	"""Chad Payroll Settings: correct CNPS pension employer rate, family allowances rate,
	and CNPS ceiling.

	PwC 2024 / Central Africa Tax Guide 2023:
	  cnps_pension_employer_rate: 7 or 7.5 → 5
	  family_allowances_rate    : 6        → 7.5
	  cnps_ceiling              : 0        → 500,000 (legal fixed ceiling XAF/month)

	Only corrects values still at the known-wrong defaults; never clobbers user edits.
	"""
	if not frappe.db.exists("DocType", "Chad Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Chad Payroll Settings", "cnps_pension_employer_rate"))
	if abs(val - 7) < 0.01 or abs(val - 7.5) < 0.01:
		corrections["cnps_pension_employer_rate"] = 5

	val = flt(frappe.db.get_single_value("Chad Payroll Settings", "family_allowances_rate"))
	if abs(val - 6) < 0.01:
		corrections["family_allowances_rate"] = 7.5

	val = flt(frappe.db.get_single_value("Chad Payroll Settings", "cnps_ceiling"))
	if abs(val) < 0.01:  # was 0 (no ceiling set)
		corrections["cnps_ceiling"] = 500000

	if corrections:
		frappe.db.set_single_value("Chad Payroll Settings", corrections)
