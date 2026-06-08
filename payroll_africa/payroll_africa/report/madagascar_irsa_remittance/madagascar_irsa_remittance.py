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
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "cnaps_employee", "label": _("CNaPS Employee (1%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "irsa", "label": _("IRSA"), "fieldtype": "Currency", "width": 150},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
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
	amounts = fetch_component_amounts(slip_names, ["CNaPS Employee", "IRSA"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		row["cnaps_employee"] = slip_amounts.get("CNaPS Employee", 0)
		row["irsa"] = slip_amounts.get("IRSA", 0)
		del row["salary_slip"]

	return data
