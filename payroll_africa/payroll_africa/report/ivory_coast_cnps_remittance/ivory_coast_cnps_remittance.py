import frappe
from frappe import _
from frappe.utils import flt

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, standard_slip_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "cnps_employee", "label": _("CNPS Employee (6.3%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "cnps_employer", "label": _("CNPS Employer (7.7%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "family_allowances", "label": _("Family Allowances (5.75%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "work_injury", "label": _("Work Injury"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "training_tax", "label": _("Training Tax (1.2%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "housing_fund", "label": _("Housing Fund (1.5%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "total_cnps", "label": _("Total CNPS"), "fieldtype": "Currency", "width": 150},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	components = [
		"CNPS Retirement Employee", "CNPS Retirement Employer",
		"CNPS Family Allowances", "Work Injury Insurance",
		"Vocational Training Tax", "Housing Construction Fund",
	]
	amounts = fetch_component_amounts(slip_names, components)

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("CNPS Retirement Employee", 0)
		empr = slip_amounts.get("CNPS Retirement Employer", 0)
		family = slip_amounts.get("CNPS Family Allowances", 0)
		injury = slip_amounts.get("Work Injury Insurance", 0)
		training = slip_amounts.get("Vocational Training Tax", 0)
		housing = slip_amounts.get("Housing Construction Fund", 0)
		row["cnps_employee"] = emp
		row["cnps_employer"] = empr
		row["family_allowances"] = family
		row["work_injury"] = injury
		row["training_tax"] = training
		row["housing_fund"] = housing
		row["total_cnps"] = emp + empr + family + injury + training + housing
		del row["salary_slip"]

	return data
