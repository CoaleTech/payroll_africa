import frappe
from frappe.utils import flt


def execute():
	"""Senegal Payroll Settings: correct AMO health ceiling to 250,000 XOF/month.

	CLEISS 2026: amo_ceiling 432,000 or 299,000 → 250,000

	Only corrects values still at the known-wrong defaults; never clobbers user edits.
	"""
	if not frappe.db.exists("DocType", "Senegal Payroll Settings"):
		return

	val = flt(frappe.db.get_single_value("Senegal Payroll Settings", "amo_ceiling"))
	if abs(val - 432000) < 1 or abs(val - 299000) < 1:
		frappe.db.set_single_value("Senegal Payroll Settings", "amo_ceiling", 250000)
