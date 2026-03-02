import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "nssf_no", "label": _("NSSF No"), "fieldtype": "Data", "width": 120},
		{"fieldname": "national_id", "label": _("National ID"), "fieldtype": "Data", "width": 120},
		{"fieldname": "nssf_employee", "label": _("Employee Contribution"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "nssf_employer", "label": _("Employer Contribution"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "total_nssf", "label": _("Total NSSF"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name,
			e.nssf_no, e.national_id,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in data:
		emp_amount = frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NSSF Employee", "parentfield": "deductions"},
			"amount",
		) or 0
		empr_amount = frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NSSF Employer", "parentfield": "deductions"},
			"amount",
		) or 0

		row["nssf_employee"] = emp_amount
		row["nssf_employer"] = empr_amount
		row["total_nssf"] = emp_amount + empr_amount
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
