import frappe
from frappe.utils import flt


def execute():
	"""Central African Republic Payroll Settings: correct CNSS employer rate and ceiling.

	Sage 2025 / Africa HR Solutions:
	  cnss_employer_rate: 14       → 19  (12% family + 3% risks + 4% pension)
	  cnss_ceiling      : 0        → 600,000 (legal fixed ceiling XAF/month)

	Only corrects values still at the known-wrong defaults; never clobbers user edits.
	"""
	if not frappe.db.exists("DocType", "Central African Republic Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Central African Republic Payroll Settings", "cnss_employer_rate"))
	if abs(val - 14) < 0.01:
		corrections["cnss_employer_rate"] = 19

	val = flt(frappe.db.get_single_value("Central African Republic Payroll Settings", "cnss_ceiling"))
	if abs(val) < 0.01:  # was 0
		corrections["cnss_ceiling"] = 600000

	if corrections:
		frappe.db.set_single_value("Central African Republic Payroll Settings", corrections)
