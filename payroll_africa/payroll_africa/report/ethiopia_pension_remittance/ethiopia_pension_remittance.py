from frappe import _

from payroll_africa.payroll_africa.report.utils import add_basic_pay, fetch_component_amounts, slip_rows


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "basic_pay", "label": _("Basic Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "pension_employee", "label": _("Pension Employee (7%)"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "pension_employer", "label": _("Pension Employer (11%)"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "total_pension", "label": _("Total Pension"), "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"))
	add_basic_pay(data)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["Pension Employee", "Pension Employer"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("Pension Employee", 0)
		empr = slip_amounts.get("Pension Employer", 0)
		row["pension_employee"] = emp
		row["pension_employer"] = empr
		row["total_pension"] = emp + empr
		del row["salary_slip"]

	return data
