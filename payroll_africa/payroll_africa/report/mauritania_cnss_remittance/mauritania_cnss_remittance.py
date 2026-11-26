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
		{"fieldname":"cnss_emp", "label":_("CNSS Employee"), "fieldtype":"Currency", "width":130},
		{"fieldname":"cnss_empr", "label":_("CNSS Employer"), "fieldtype":"Currency", "width":130},
		{"fieldname":"cnam_emp", "label":_("CNAM Health Employee"), "fieldtype":"Currency", "width":130},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ['CNSS Employee', 'CNSS Employer', 'CNAM Health Employee'])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		row["cnss_emp"] = slip_amounts.get("CNSS Employee", 0)
		row["cnss_empr"] = slip_amounts.get("CNSS Employer", 0)
		row["cnam_emp"] = slip_amounts.get("CNAM Health Employee", 0)
		del row["salary_slip"]

	return data
