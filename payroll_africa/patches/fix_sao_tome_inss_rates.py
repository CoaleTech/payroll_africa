import frappe
from frappe.utils import flt


def execute():
	"""Sao Tome and Principe Payroll Settings: correct INSS rates per Decree-Law 1/2025.

	Decree-Law 1/2025 (7 Jan 2025), Miranda Law Firm alert:
	  inss_employee_rate: 8 → 5
	  inss_employer_rate: 12 → 7

	Only corrects values when BOTH still equal the old rates; never clobbers user edits.
	"""
	if not frappe.db.exists("DocType", "Sao Tome and Principe Payroll Settings"):
		return

	emp = flt(frappe.db.get_single_value("Sao Tome and Principe Payroll Settings", "inss_employee_rate"))
	empr = flt(frappe.db.get_single_value("Sao Tome and Principe Payroll Settings", "inss_employer_rate"))

	if abs(emp - 8) < 0.01 and abs(empr - 12) < 0.01:
		frappe.db.set_single_value("Sao Tome and Principe Payroll Settings", {
			"inss_employee_rate": 5,
			"inss_employer_rate": 7,
		})
