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
		{"fieldname": "net_pay", "label": _("Monthly Take-Home"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "lst_amount", "label": _("LST Deducted"), "fieldtype": "Currency", "width": 130},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "net_pay"))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["LST"])

	for row in data:
		row["lst_amount"] = amounts.get(row.salary_slip, {}).get("LST", 0)
		del row["salary_slip"]

	return data
