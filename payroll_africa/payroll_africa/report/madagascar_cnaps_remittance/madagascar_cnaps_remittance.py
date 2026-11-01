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
		{"fieldname": "cnaps_employee", "label": _("CNaPS Employee (1%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "cnaps_employer", "label": _("CNaPS Employer (13%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "health_employee", "label": _("Health Employee (1%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "health_employer", "label": _("Health Employer (5%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "fmfp", "label": _("FMFP Training Fund (1%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "total_cnaps", "label": _("Total CNaPS"), "fieldtype": "Currency", "width": 150},
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
	amounts = fetch_component_amounts(slip_names, [
		"CNaPS Employee", "CNaPS Employer",
		"Health Insurance Employee", "Health Insurance Employer",
		"FMFP Training Fund",
	])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		ce = slip_amounts.get("CNaPS Employee", 0)
		cr = slip_amounts.get("CNaPS Employer", 0)
		he = slip_amounts.get("Health Insurance Employee", 0)
		hr = slip_amounts.get("Health Insurance Employer", 0)
		fmfp = slip_amounts.get("FMFP Training Fund", 0)
		row["cnaps_employee"] = ce
		row["cnaps_employer"] = cr
		row["health_employee"] = he
		row["health_employer"] = hr
		row["fmfp"] = fmfp
		row["total_cnaps"] = ce + cr + he + hr + fmfp
		del row["salary_slip"]

	return data
