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
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nhis_employee", "label": _("Employee (5%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nhis_employer", "label": _("Employer (10%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_nhis", "label": _("Total (15%)"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in data:
		emp = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NHIS Employee NG", "parentfield": "deductions"},
			"amount",
		))
		empr = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NHIS Employer NG", "parentfield": "deductions"},
			"amount",
		))

		row["nhis_employee"] = emp
		row["nhis_employer"] = empr
		row["total_nhis"] = emp + empr
		del row["salary_slip"]

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
