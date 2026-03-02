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
		{"fieldname": "zm_napsa_no", "label": _("NAPSA No"), "fieldtype": "Data", "width": 130},
		{"fieldname": "zm_nrc", "label": _("NRC"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "napsa_employee", "label": _("Employee (5%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "napsa_employer", "label": _("Employer (5%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_napsa", "label": _("Total NAPSA"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.zm_napsa_no, e.zm_nrc, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in data:
		emp = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NAPSA Employee ZM", "parentfield": "deductions"},
			"amount",
		))
		empr = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NAPSA Employer ZM", "parentfield": "deductions"},
			"amount",
		))

		row["napsa_employee"] = emp
		row["napsa_employer"] = empr
		row["total_napsa"] = emp + empr
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
