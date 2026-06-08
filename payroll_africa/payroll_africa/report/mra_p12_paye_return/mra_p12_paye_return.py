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
		{"fieldname": "mw_tax_no", "label": _("Tax No"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "pension_deduction", "label": _("Pension Deduction"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "taxable_pay", "label": _("Taxable Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.mw_tax_no, ss.name as salary_slip
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
	amounts = fetch_component_amounts(slip_names, ["Pension Employee MW", "PAYE MW"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		pension = slip_amounts.get("Pension Employee MW", 0)
		row["pension_deduction"] = pension
		row["taxable_pay"] = flt(row.gross_pay) - pension
		row["paye"] = slip_amounts.get("PAYE MW", 0)
		del row["salary_slip"]

	return data
