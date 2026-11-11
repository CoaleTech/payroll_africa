"""Patch: correct Comoros CNSS rates and seed PIT threshold.

Comoros CNSS statutory rates:
  Employee: 3.5% (was defaulted to 3%)
  Employer: 10.5% (was defaulted to 9%)

PIT-free threshold: 360,000 KMF/year (was defaulted to 0).

Only updates values still at the stale defaults.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Comoros Payroll Settings"):
        return

    updates = {}

    current_emp = frappe.db.get_single_value("Comoros Payroll Settings", "cnss_employee_rate")
    if current_emp is None or float(current_emp or 0) == 3.0:
        updates["cnss_employee_rate"] = 3.5

    current_empr = frappe.db.get_single_value("Comoros Payroll Settings", "cnss_employer_rate")
    if current_empr is None or float(current_empr or 0) == 9.0:
        updates["cnss_employer_rate"] = 10.5

    current_pit = frappe.db.get_single_value("Comoros Payroll Settings", "pit_threshold")
    if current_pit is None or float(current_pit or 0) == 0.0:
        updates["pit_threshold"] = 360000

    if updates:
        for field, value in updates.items():
            frappe.db.set_single_value("Comoros Payroll Settings", field, value)
        frappe.db.commit()
