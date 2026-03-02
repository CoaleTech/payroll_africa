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
		{"fieldname": "ng_nhf_no", "label": _("NHF No"), "fieldtype": "Data", "width": 130},
		{"fieldname": "basic_salary", "label": _("Basic Salary"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nhf_amount", "label": _("NHF (2.5%)"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name,
			e.ng_nhf_no, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in data:
		basic = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "Basic Salary", "parentfield": "earnings"},
			"amount",
		))
		nhf = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NHF NG", "parentfield": "deductions"},
			"amount",
		))

		row["basic_salary"] = basic
		row["nhf_amount"] = nhf
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
