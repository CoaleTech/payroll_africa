import frappe
from frappe import _
from frappe.utils import flt, getdate
import calendar

MONTHS = [
	"April", "May", "June", "July", "August", "September",
	"October", "November", "December", "January", "February", "March",
]


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "pension_deduction", "label": _("Pension Deduction"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "taxable_pay", "label": _("Taxable Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	if not filters.get("employee") or not filters.get("fiscal_year"):
		return []

	fiscal_year = frappe.get_doc("Fiscal Year", filters["fiscal_year"])
	year_start = getdate(fiscal_year.year_start_date)
	year_end = getdate(fiscal_year.year_end_date)

	data = []
	month_numbers = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]

	for idx, month_name in enumerate(MONTHS):
		month_num = month_numbers[idx]
		year = year_start.year if month_num >= 4 else year_start.year + 1
		last_day = calendar.monthrange(year, month_num)[1]
		month_start = getdate(f"{year}-{month_num:02d}-01")
		month_end = getdate(f"{year}-{month_num:02d}-{last_day}")

		if month_start > year_end or month_end < year_start:
			continue

		row = get_month_data(filters, month_name, month_start, month_end)
		data.append(row)

	return data


def get_month_data(filters, month_name, month_start, month_end):
	row = {"month": month_name}

	salary_slip = frappe.db.sql(
		"""
		SELECT name, gross_pay
		FROM `tabSalary Slip`
		WHERE docstatus = 1
			AND employee = %(employee)s
			AND start_date >= %(month_start)s
			AND end_date <= %(month_end)s
			AND company = %(company)s
		LIMIT 1
		""",
		{"employee": filters["employee"], "month_start": month_start, "month_end": month_end, "company": filters["company"]},
		as_dict=True,
	)

	if not salary_slip:
		return row

	slip = salary_slip[0]
	row["gross_pay"] = flt(slip.gross_pay)

	pension = flt(frappe.db.get_value(
		"Salary Detail",
		{"parent": slip.name, "salary_component": "Pension Employee MW", "parentfield": "deductions"},
		"amount",
	))
	paye = flt(frappe.db.get_value(
		"Salary Detail",
		{"parent": slip.name, "salary_component": "PAYE MW", "parentfield": "deductions"},
		"amount",
	))

	row["pension_deduction"] = pension
	row["taxable_pay"] = flt(slip.gross_pay) - pension
	row["paye"] = paye

	return row
