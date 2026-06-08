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
		{"fieldname": "national_id", "label": _("National ID"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "employee_levy", "label": _("Employee Levy"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "employer_levy", "label": _("Employer Levy"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_levy", "label": _("Total Levy"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.national_id,
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
	amounts = fetch_component_amounts(slip_names, ["Housing Levy", "Employer Housing Levy"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp_levy = slip_amounts.get("Housing Levy", 0)
		empr_levy = slip_amounts.get("Employer Housing Levy", 0)
		row["employee_levy"] = emp_levy
		row["employer_levy"] = empr_levy
		row["total_levy"] = emp_levy + empr_levy
		del row["salary_slip"]

	return data
