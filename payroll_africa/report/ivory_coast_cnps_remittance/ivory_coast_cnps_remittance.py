import frappe
from frappe import _
from frappe.utils import flt, formatdate

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, standard_slip_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "cnps_retirement_employee", "label": _("CNPS Retirement Employee"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "cnps_retirement_employer", "label": _("CNPS Retirement Employer"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "cnps_family_allowances", "label": _("CNPS Family Allowances"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "work_injury_insurance", "label": _("Work Injury Insurance"), "fieldtype": "Currency", "width": 160},
		{"fieldname": "total_cnps", "label": _("Total CNPS"), "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay, ss.start_date,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee, ss.start_date
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(
		slip_names,
		["CNPS Retirement Employee", "CNPS Retirement Employer", "CNPS Family Allowances", "Work Injury Insurance"],
	)

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		ret_emp = slip_amounts.get("CNPS Retirement Employee", 0)
		ret_empr = slip_amounts.get("CNPS Retirement Employer", 0)
		fa = slip_amounts.get("CNPS Family Allowances", 0)
		wii = slip_amounts.get("Work Injury Insurance", 0)
		row["cnps_retirement_employee"] = ret_emp
		row["cnps_retirement_employer"] = ret_empr
		row["cnps_family_allowances"] = fa
		row["work_injury_insurance"] = wii
		row["total_cnps"] = ret_emp + ret_empr + fa + wii
		row["month"] = formatdate(row.start_date, "MMM-YYYY")
		del row["salary_slip"]
		del row["start_date"]

	return data
