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
		{"fieldname": "ng_tin", "label": _("TIN"), "fieldtype": "Data", "width": 120},
		{"fieldname": "ng_payer_id", "label": _("Payer ID"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "pension_deduction", "label": _("Pension (8%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nhf", "label": _("NHF (2.5%)"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.ng_tin, e.ng_payer_id, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in data:
		pension = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "Pension Employee NG", "parentfield": "deductions"},
			"amount",
		))
		nhf = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "NHF NG", "parentfield": "deductions"},
			"amount",
		))
		paye = flt(frappe.db.get_value(
			"Salary Detail",
			{"parent": row.salary_slip, "salary_component": "PAYE NG", "parentfield": "deductions"},
			"amount",
		))

		row["pension_deduction"] = pension
		row["nhf"] = nhf
		row["taxable_income"] = flt(row.gross_pay) - pension - nhf
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
