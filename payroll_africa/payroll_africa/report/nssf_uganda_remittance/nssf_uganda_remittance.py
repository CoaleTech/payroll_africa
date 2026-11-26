from frappe import _

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, slip_rows


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "ug_nssf_no", "label": _("NSSF Member No"), "fieldtype": "Data", "width": 140},
		{"fieldname": "gross_pay", "label": _("Gross Monthly Wage"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "nssf_employee", "label": _("Employee (5%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nssf_employer", "label": _("Employer (10%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_nssf", "label": _("Total Contribution"), "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"), ("ug_nssf_no",))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["NSSF Employee UG", "NSSF Employer UG"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("NSSF Employee UG", 0)
		empr = slip_amounts.get("NSSF Employer UG", 0)
		row["nssf_employee"] = emp
		row["nssf_employer"] = empr
		row["total_nssf"] = emp + empr
		del row["salary_slip"]

	return data
