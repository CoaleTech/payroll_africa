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
		{"fieldname": "ng_rsa_pin", "label": _("RSA PIN"), "fieldtype": "Data", "width": 130},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "pension_employee", "label": _("Employee (8%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "pension_employer", "label": _("Employer (10%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_pension", "label": _("Total (18%)"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.ng_rsa_pin, ss.name as salary_slip
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
	amounts = fetch_component_amounts(slip_names, ["Pension Employee NG", "Pension Employer NG"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("Pension Employee NG", 0)
		empr = slip_amounts.get("Pension Employer NG", 0)
		row["pension_employee"] = emp
		row["pension_employer"] = empr
		row["total_pension"] = emp + empr
		del row["salary_slip"]

	return data
