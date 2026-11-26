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
		{"fieldname": "national_id", "label": _("National ID"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "employee_levy", "label": _("Employee Levy"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "employer_levy", "label": _("Employer Levy"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_levy", "label": _("Total Levy"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"), ("national_id",))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["Housing Levy", "Employer Housing Levy"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp_levy = slip_amounts.get("Housing Levy", 0)
		empr_levy = slip_amounts.get("Employer Housing Levy", 0)
		row["employee_levy"] = emp_levy
		row["employer_levy"] = empr_levy
		row["total_levy"] = emp_levy + empr_levy
		del row["salary_slip"]

	return data
