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
		{"fieldname": "mz_inss_no", "label": _("INSS No"), "fieldtype": "Data", "width": 130},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "inss_employee", "label": _("Employee (3%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "inss_employer", "label": _("Employer (4%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_inss", "label": _("Total (7%)"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"), ("mz_inss_no",))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["INSS Employee MZ", "INSS Employer MZ"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("INSS Employee MZ", 0)
		empr = slip_amounts.get("INSS Employer MZ", 0)
		row["inss_employee"] = emp
		row["inss_employer"] = empr
		row["total_inss"] = emp + empr
		del row["salary_slip"]

	return data
