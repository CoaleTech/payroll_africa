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
		{"fieldname": "bi_inss_no", "label": _("INSS No"), "fieldtype": "Data", "width": 130},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "inss_employee", "label": _("Employee Pension (4%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "inss_employer", "label": _("Employer Pension (6%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "work_injury", "label": _("Employer Risk (3%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "total_inss", "label": _("Total INSS"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.bi_inss_no, ss.name as salary_slip
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
	amounts = fetch_component_amounts(slip_names, ["INSS Employee BI", "INSS Employer BI", "Work Injury BI"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("INSS Employee BI", 0)
		empr = slip_amounts.get("INSS Employer BI", 0)
		risk = slip_amounts.get("Work Injury BI", 0)
		row["inss_employee"] = emp
		row["inss_employer"] = empr
		row["work_injury"] = risk
		row["total_inss"] = emp + empr + risk
		del row["salary_slip"]

	return data
