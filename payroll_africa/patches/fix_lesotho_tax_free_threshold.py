import frappe
from frappe.utils import flt


def execute():
	"""Lesotho: set tax_free_threshold to 0 — the LSL 21,600 default has no statutory basis.

	Source: RSL 2025/26 circular — Lesotho uses a credit-based system (20%/30% bands with
	a M11,640/year credit) and does not use a zero-rate income threshold.  The calculator
	already treats 0 or None as "no threshold" (lesotho.py:36-37).

	Only rewrites when still at the old known-wrong default of 21,600.
	"""
	if not frappe.db.exists("DocType", "Lesotho Payroll Settings"):
		return

	current = frappe.db.get_value(
		"Lesotho Payroll Settings", "Lesotho Payroll Settings", "tax_free_threshold"
	)
	if current is not None and flt(current) == 21600:
		frappe.db.set_value(
			"Lesotho Payroll Settings", "Lesotho Payroll Settings", "tax_free_threshold", 0
		)
