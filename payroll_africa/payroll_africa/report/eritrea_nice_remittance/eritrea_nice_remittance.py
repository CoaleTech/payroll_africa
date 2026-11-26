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
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname":"nice_emp", "label":_("NICE Employee"), "fieldtype":"Currency", "width":130},
		{"fieldname":"nice_empr", "label":_("NICE Employer"), "fieldtype":"Currency", "width":130},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ['NICE Employee', 'NICE Employer'])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		row["nice_emp"] = slip_amounts.get("NICE Employee", 0)
		row["nice_empr"] = slip_amounts.get("NICE Employer", 0)
		del row["salary_slip"]

	return data
