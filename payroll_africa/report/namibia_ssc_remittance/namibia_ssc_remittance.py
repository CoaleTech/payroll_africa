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
		{"fieldname": "social_security_employer", "label": _("Social Security Employer"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "employees_compensation", "label": _("Employees Compensation"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "vet_levy", "label": _("VET Levy"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "total_ssc", "label": _("Total SSC"), "fieldtype": "Currency", "width": 140},
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
	amounts = fetch_component_amounts(
		slip_names,
		["Social Security Employee", "Social Security Employer", "Employees Compensation", "VET Levy"],
	)

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		ssc_emp = slip_amounts.get("Social Security Employee", 0)
		ssc_empr = slip_amounts.get("Social Security Employer", 0)
		ec = slip_amounts.get("Employees Compensation", 0)
		vet = slip_amounts.get("VET Levy", 0)
		row["social_security_employee"] = ssc_emp
		row["social_security_employer"] = ssc_empr
		row["employees_compensation"] = ec
		row["vet_levy"] = vet
		row["total_ssc"] = ssc_emp + ssc_empr + ec + vet
		row["month"] = formatdate(row.start_date, "MMM-YYYY")
		del row["salary_slip"]
		del row["start_date"]

	return data
