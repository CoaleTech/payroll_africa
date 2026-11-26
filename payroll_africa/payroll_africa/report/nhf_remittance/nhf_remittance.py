from frappe import _

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, slip_rows


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "ng_nhf_no", "label": _("NHF No"), "fieldtype": "Data", "width": 130},
		{"fieldname": "basic_salary", "label": _("Basic Salary"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nhf_amount", "label": _("NHF (2.5%)"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name"), ("ng_nhf_no",))

	slip_names = [r.salary_slip for r in data]
	earnings = fetch_component_amounts(slip_names, ["Basic Salary"], parentfield="earnings")
	deductions = fetch_component_amounts(slip_names, ["NHF NG"])

	for row in data:
		row["basic_salary"] = earnings.get(row.salary_slip, {}).get("Basic Salary", 0)
		row["nhf_amount"] = deductions.get(row.salary_slip, {}).get("NHF NG", 0)
		del row["salary_slip"]

	return data
