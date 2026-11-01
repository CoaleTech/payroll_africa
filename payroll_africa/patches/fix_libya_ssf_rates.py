"""Patch: correct Libya SSF rates and solidarity_fund_rate.

PwC Libya Tax Summary 2026 shows updated Social Security Fund rates:
  Employee: 5.125% (was 3.75% under Law 13/1980)
  Employer: 14.35% (was 11.25% under Law 13/1980)

The solidarity_fund_rate was set to 3% default but the calculator always
applied 1%; corrected to 1%.

Only updates values still at the stale defaults.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Libya Payroll Settings"):
        return

    updates = {}
    current_emp = frappe.db.get_single_value("Libya Payroll Settings", "ssf_employee_rate")
    if current_emp is None or float(current_emp or 0) == 3.75:
        updates["ssf_employee_rate"] = 5.125

    current_empr = frappe.db.get_single_value("Libya Payroll Settings", "ssf_employer_rate")
    if current_empr is None or float(current_empr or 0) == 11.25:
        updates["ssf_employer_rate"] = 14.35

    current_sol = frappe.db.get_single_value("Libya Payroll Settings", "solidarity_fund_rate")
    if current_sol is None or float(current_sol or 0) == 3.0:
        updates["solidarity_fund_rate"] = 1.0

    if updates:
        for field, value in updates.items():
            frappe.db.set_single_value("Libya Payroll Settings", field, value)
        frappe.db.commit()
