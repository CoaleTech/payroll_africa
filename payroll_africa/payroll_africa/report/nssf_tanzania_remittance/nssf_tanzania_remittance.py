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
		{"fieldname": "tz_nssf_no", "label": _("NSSF Member No"), "fieldtype": "Data", "width": 140},
		{"fieldname": "gross_pay", "label": _("Gross Monthly Wage"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "nssf_employee", "label": _("Employee (10%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nssf_employer", "label": _("Employer (10%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_nssf", "label": _("Total Contribution"), "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.tz_nssf_no, ss.name as salary_slip
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
			{"parent": row.salary_slip, "salary_component": "NSSF Employee TZ", "parentfield": "deductions"},
			"amount",
		))
		empr = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NSSF Employer TZ", "parentfield": "deductions"},
			"amount",
		))

		row["nssf_employee"] = emp
		row["nssf_employer"] = empr
		row["total_nssf"] = emp + empr
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
