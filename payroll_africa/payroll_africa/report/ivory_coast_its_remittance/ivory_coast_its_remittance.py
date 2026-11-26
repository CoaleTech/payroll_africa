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
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "standard_deduction", "label": _("Standard Deduction (20%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "its", "label": _("ITS"), "fieldtype": "Currency", "width": 150},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["ITS"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		row["its"] = slip_amounts.get("ITS", 0)
		row["standard_deduction"] = flt(row.gross_pay * 0.20, 2)
		del row["salary_slip"]

	return data
