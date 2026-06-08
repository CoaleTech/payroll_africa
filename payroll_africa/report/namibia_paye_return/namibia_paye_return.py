import frappe
from frappe import _
from frappe.utils import flt, formatdate

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, standard_slip_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "social_security_employee", "label": _("Social Security Employee"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay, ss.start_date,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee, ss.start_date
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["Social Security Employee", "PAYE"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		ssc = slip_amounts.get("Social Security Employee", 0)
		row["social_security_employee"] = ssc
		row["taxable_income"] = flt(row.gross_pay) - ssc
		row["paye"] = slip_amounts.get("PAYE", 0)
		row["month"] = formatdate(row.start_date, "MMM-YYYY")
		del row["salary_slip"]
		del row["start_date"]

	return data
