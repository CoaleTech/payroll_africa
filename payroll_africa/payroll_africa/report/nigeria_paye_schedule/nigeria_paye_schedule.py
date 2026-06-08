import frappe
from frappe import _
from frappe.utils import flt

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, standard_slip_conditions


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
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.ng_tin, e.ng_payer_id, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["Pension Employee NG", "NHF NG", "PAYE NG"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		pension = slip_amounts.get("Pension Employee NG", 0)
		nhf = slip_amounts.get("NHF NG", 0)
		row["pension_deduction"] = pension
		row["nhf"] = nhf
		row["taxable_income"] = flt(row.gross_pay) - pension - nhf
		row["paye"] = slip_amounts.get("PAYE NG", 0)
		del row["salary_slip"]

	return data
