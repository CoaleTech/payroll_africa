import frappe
from frappe import _
from frappe.utils import flt


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
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee,
			ss.employee_name,
			sd.salary_component AS component,
			sd.amount,
			DATE_FORMAT(ss.end_date, '%%Y-%%m') AS month
		FROM `tabSalary Slip` ss
		INNER JOIN `tabSalary Detail` sd ON sd.parent = ss.name
		WHERE ss.docstatus = 1
			AND sd.parentfield = 'deductions'
			AND sd.salary_component IN ('UIF Employee', 'UIF Employer', 'SDL')
		"""
		+ conditions
		+ """
		ORDER BY ss.end_date, ss.employee, sd.salary_component
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["amount"] = flt(row.amount)

	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND ss.company = %(company)s"
	if filters.get("from_date"):
		conditions += " AND ss.start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND ss.end_date <= %(to_date)s"
	return conditions
