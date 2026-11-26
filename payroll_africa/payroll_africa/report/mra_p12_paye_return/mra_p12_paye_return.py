from frappe import _
from frappe.utils import flt

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, slip_rows


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
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"), ("mw_tax_no",))

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
