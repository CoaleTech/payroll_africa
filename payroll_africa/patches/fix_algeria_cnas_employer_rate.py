"""Patch: correct Algeria CNAS employer contribution rate from 25.5% to 26%.

The statutory CNAS employer rate (all branches) is 26% per CNAS Algeria official
schedule. The original DocType default of 25.5% was a rounding error.

Only updates when the value is still at the stale 25.5 default.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Algeria Payroll Settings"):
        return

    current = frappe.db.get_single_value("Algeria Payroll Settings", "cnas_employer_rate")
    if current is None or float(current or 0) == 25.5:
        frappe.db.set_single_value("Algeria Payroll Settings", "cnas_employer_rate", 26)
        frappe.db.commit()
