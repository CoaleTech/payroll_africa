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
		{"fieldname": "bi_nif", "label": _("NIF"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "inss_employee", "label": _("INSS Employee (4%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.bi_nif, ss.name as salary_slip
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
	amounts = fetch_component_amounts(slip_names, ["INSS Employee BI", "PAYE BI"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		inss = slip_amounts.get("INSS Employee BI", 0)
		row["inss_employee"] = inss
		row["taxable_income"] = flt(row.gross_pay) - inss
		row["paye"] = slip_amounts.get("PAYE BI", 0)
		del row["salary_slip"]

	return data
