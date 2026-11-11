"""Patch: correct Egypt personal_exemption default from 15000 to 20000.

The statutory annual personal tax exemption (Article 7, ITA Egypt, amended 2023) is
EGP 20,000/year. The original DocType default was stale at EGP 15,000.

Only updates the value when it is still at the wrong default (15,000); leaves
any deliberate operator customisation alone.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Egypt Payroll Settings"):
        return

    current = frappe.db.get_single_value("Egypt Payroll Settings", "personal_exemption")
    if current is None or float(current or 0) == 15000.0:
        frappe.db.set_single_value("Egypt Payroll Settings", "personal_exemption", 20000)
        frappe.db.commit()
