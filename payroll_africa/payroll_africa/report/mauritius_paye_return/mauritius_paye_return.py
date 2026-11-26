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
		{"fieldname":"paye", "label":_("PAYE"), "fieldtype":"Currency", "width":130},
		{"fieldname":"csg", "label":_("CSG"), "fieldtype":"Currency", "width":130},
		{"fieldname":"nsf_emp", "label":_("NSF Employee"), "fieldtype":"Currency", "width":130},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay"))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ['PAYE', 'CSG', 'NSF Employee'])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		row["paye"] = slip_amounts.get("PAYE", 0)
		row["csg"] = slip_amounts.get("CSG", 0)
		row["nsf_emp"] = slip_amounts.get("NSF Employee", 0)
		del row["salary_slip"]

	return data
