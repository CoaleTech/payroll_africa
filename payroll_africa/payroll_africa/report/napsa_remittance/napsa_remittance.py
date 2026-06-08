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
		{"fieldname": "zm_napsa_no", "label": _("NAPSA No"), "fieldtype": "Data", "width": 130},
		{"fieldname": "zm_nrc", "label": _("NRC"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "napsa_employee", "label": _("Employee (5%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "napsa_employer", "label": _("Employer (5%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_napsa", "label": _("Total NAPSA"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.zm_napsa_no, e.zm_nrc, ss.name as salary_slip
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
	amounts = fetch_component_amounts(slip_names, ["NAPSA Employee ZM", "NAPSA Employer ZM"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("NAPSA Employee ZM", 0)
		empr = slip_amounts.get("NAPSA Employer ZM", 0)
		row["napsa_employee"] = emp
		row["napsa_employer"] = empr
		row["total_napsa"] = emp + empr
		del row["salary_slip"]

	return data
