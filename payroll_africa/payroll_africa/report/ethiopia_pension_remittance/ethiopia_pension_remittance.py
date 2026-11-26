from frappe import _
from frappe.utils import flt

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, slip_rows


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "basic_pay", "label": _("Basic Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "pension_employee", "label": _("Pension Employee (7%)"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "pension_employer", "label": _("Pension Employer (11%)"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "total_pension", "label": _("Total Pension"), "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name"))

	slip_names = [r.salary_slip for r in data]
	basic_amounts = fetch_component_amounts(slip_names, ["Basic Salary"], parentfield="earnings")
	pension_amounts = fetch_component_amounts(slip_names, ["Pension Employee", "Pension Employer"])

	for row in data:
		basic = basic_amounts.get(row.salary_slip, {}) or {}
		pen = pension_amounts.get(row.salary_slip, {}) or {}
		row["basic_pay"] = flt(basic.get("Basic Salary", 0))
		emp = flt(pen.get("Pension Employee", 0))
		empr = flt(pen.get("Pension Employer", 0))
		row["pension_employee"] = emp
		row["pension_employer"] = empr
		row["total_pension"] = emp + empr
		del row["salary_slip"]

	return data
