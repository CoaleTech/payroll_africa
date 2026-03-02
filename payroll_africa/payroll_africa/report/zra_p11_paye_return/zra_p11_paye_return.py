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
		{"fieldname": "zm_tpin", "label": _("TPIN"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "napsa_deduction", "label": _("NAPSA Deduction"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.zm_tpin, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in data:
		napsa = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NAPSA Employee ZM", "parentfield": "deductions"},
			"amount",
		))
		paye = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "PAYE ZM", "parentfield": "deductions"},
			"amount",
		))

		row["napsa_deduction"] = napsa
		row["taxable_income"] = flt(row.gross_pay) - napsa
		row["paye"] = paye
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
