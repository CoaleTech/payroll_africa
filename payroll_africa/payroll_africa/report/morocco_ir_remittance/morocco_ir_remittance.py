from frappe import _

from payroll_africa.payroll_africa.report.utils import component_lines


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "component", "label": _("Component"), "fieldtype": "Data", "width": 150},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
	]


def get_data(filters):
	return component_lines(filters, ("IR",))
