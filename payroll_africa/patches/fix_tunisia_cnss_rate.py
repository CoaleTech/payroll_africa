"""Patch: correct Tunisia CNSS employee rate from 9.18% to 9.68%.

LF2025 (Law 48/2024) raised the employee CNSS rate from 9.18% to 9.68%
effective 1 January 2025.

Only updates when the value is still at the stale 9.18 default.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Tunisia Payroll Settings"):
        return

    current = frappe.db.get_single_value("Tunisia Payroll Settings", "cnss_employee_rate")
    if current is None or float(current or 0) == 9.18:
        frappe.db.set_single_value("Tunisia Payroll Settings", "cnss_employee_rate", 9.68)
        frappe.db.commit()
