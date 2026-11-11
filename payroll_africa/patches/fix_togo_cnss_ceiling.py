import frappe
from frappe.utils import flt


def execute():
	"""Togo Payroll Settings: remove CNSS/INAM ceiling (no legal ceiling per CLEISS 2026).

	cnss_ceiling: 500,000 → 0  (0 means uncapped in the updated calculator)

	Only corrects values still at the known-wrong default; never clobbers user edits.
	"""
	if not frappe.db.exists("DocType", "Togo Payroll Settings"):
		return

	val = flt(frappe.db.get_single_value("Togo Payroll Settings", "cnss_ceiling"))
	if abs(val - 500000) < 1:
		frappe.db.set_single_value("Togo Payroll Settings", "cnss_ceiling", 0)
