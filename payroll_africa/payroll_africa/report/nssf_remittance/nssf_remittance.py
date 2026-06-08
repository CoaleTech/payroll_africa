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
		{"fieldname": "nssf_no", "label": _("NSSF No"), "fieldtype": "Data", "width": 120},
		{"fieldname": "national_id", "label": _("National ID"), "fieldtype": "Data", "width": 120},
		{"fieldname": "nssf_employee", "label": _("Employee Contribution"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "nssf_employer", "label": _("Employer Contribution"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "total_nssf", "label": _("Total NSSF"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name,
			e.nssf_no, e.national_id,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["NSSF Employee", "NSSF Employer"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("NSSF Employee", 0)
		empr = slip_amounts.get("NSSF Employer", 0)
		row["nssf_employee"] = emp
		row["nssf_employer"] = empr
		row["total_nssf"] = emp + empr
		del row["salary_slip"]

	return data
