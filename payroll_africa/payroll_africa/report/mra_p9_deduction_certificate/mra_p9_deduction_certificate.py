import frappe
from frappe import _
from frappe.utils import flt, getdate
import calendar
import datetime

# Month iteration is derived at runtime from the selected Fiscal Year document
# so the report works for any fiscal-year start month (July-June, April-March,
# January-December, etc.) without hard-coding the calendar order.


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
	curr_year = year_start.year
	curr_month = year_start.month

	for _i in range(12):  # a fiscal year spans at most 12 calendar months
		last_day = calendar.monthrange(curr_year, curr_month)[1]
		month_start = datetime.date(curr_year, curr_month, 1)
		month_end = datetime.date(curr_year, curr_month, last_day)

		if month_start > year_end:
			break

		month_name = calendar.month_name[curr_month]
		row = get_month_data(filters, month_name, month_start, month_end)
		data.append(row)

		curr_month += 1
		if curr_month > 12:
			curr_month = 1
			curr_year += 1

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
	row["gross_pay"] = flt(slip["gross_pay"])

	pension = flt(frappe.db.get_value(
		"Salary Detail",
		{"parent": slip["name"], "salary_component": "Pension Employee MW", "parentfield": "deductions"},
		"amount",
	))
	paye = flt(frappe.db.get_value(
		"Salary Detail",
		{"parent": slip["name"], "salary_component": "PAYE MW", "parentfield": "deductions"},
		"amount",
	))

	row["pension_deduction"] = pension
	row["taxable_pay"] = flt(slip["gross_pay"]) - pension
	row["paye"] = paye

	return row
