import frappe
from frappe.utils import flt


def execute():
	"""Senegal Payroll Settings: correct IPRES ceiling, CSS rates, and add CSS Health Employee component.

	Wrong defaults shipped in DocType JSON:
	  ipres_ceiling          : 299,000 → 432,000  (6 × SMIG 72,000)
	  ipres_ceiling_multiplier: 4      → 6
	  css_employee_rate      : 3.0     → 0        (CSS employee is employer-only; configurable)
	  css_employer_rate      : 5.0     → 7.0      (correct statutory employer rate)
	  css_ceiling            : 299,000 → 432,000
	Also creates "CSS Health Employee" salary component if missing.
	"""
	if not frappe.db.exists("DocType", "Senegal Payroll Settings"):
		return

	corrections = {}

	val = flt(frappe.db.get_single_value("Senegal Payroll Settings", "ipres_ceiling"))
	if abs(val - 299000) < 1:
		corrections["ipres_ceiling"] = 432000

	val = flt(frappe.db.get_single_value("Senegal Payroll Settings", "ipres_ceiling_multiplier"))
	if abs(val - 4) < 0.01:
		corrections["ipres_ceiling_multiplier"] = 6

	val = flt(frappe.db.get_single_value("Senegal Payroll Settings", "css_employee_rate"))
	if abs(val - 3.0) < 0.01:
		corrections["css_employee_rate"] = 0

	val = flt(frappe.db.get_single_value("Senegal Payroll Settings", "css_employer_rate"))
	if abs(val - 5.0) < 0.01:
		corrections["css_employer_rate"] = 7

	val = flt(frappe.db.get_single_value("Senegal Payroll Settings", "css_ceiling"))
	if abs(val - 299000) < 1:
		corrections["css_ceiling"] = 432000

	if corrections:
		frappe.db.set_single_value("Senegal Payroll Settings", corrections)

	# Create CSS Health Employee salary component if it does not exist yet.
	if not frappe.db.exists("Salary Component", "CSS Health Employee"):
		comp = frappe.get_doc({
			"doctype": "Salary Component",
			"salary_component": "CSS Health Employee",
			"salary_component_abbr": "CSSe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
		})
		comp.flags.ignore_permissions = True
		comp.insert()

	# Add CSS Health Employee to Senegal Payroll Template if missing.
	if frappe.db.exists("Salary Structure", "Senegal Payroll Template"):
		existing = frappe.db.get_value(
			"Salary Detail",
			{
				"parent": "Senegal Payroll Template",
				"parenttype": "Salary Structure",
				"salary_component": "CSS Health Employee",
			},
			"name",
		)
		if not existing:
			structure = frappe.get_doc("Salary Structure", "Senegal Payroll Template")
			structure.append("deductions", {
				"salary_component": "CSS Health Employee",
				"abbr": "CSSe",
			})
			structure.flags.ignore_permissions = True
			structure.save()
