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
		{"fieldname": "zm_tpin", "label": _("TPIN"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "napsa_deduction", "label": _("NAPSA Deduction"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"), ("zm_tpin",))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["NAPSA Employee ZM", "PAYE ZM"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		napsa = slip_amounts.get("NAPSA Employee ZM", 0)
		row["napsa_deduction"] = napsa
		row["taxable_income"] = flt(row.gross_pay)  # NAPSA no longer deductible for PAYE (2025+)
		row["paye"] = slip_amounts.get("PAYE ZM", 0)
		del row["salary_slip"]

	return data
