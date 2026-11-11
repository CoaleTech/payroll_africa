"""Patch: correct Morocco dependent allowance from MAD 500 to MAD 600.

Loi de Finances 50-25 (2026) sets the annual IR reduction per dependent at
MAD 600. The calculator stores a monthly figure (multiplied by 12 internally).
The original default of 500 was stale.

Only updates when the value is still at the stale 500 default.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Morocco Payroll Settings"):
        return

    current = frappe.db.get_single_value("Morocco Payroll Settings", "dependent_allowance")
    if current is None or float(current or 0) == 500.0:
        frappe.db.set_single_value("Morocco Payroll Settings", "dependent_allowance", 600)
        frappe.db.commit()
