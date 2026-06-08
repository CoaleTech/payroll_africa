import frappe
from frappe import _
from frappe.utils import flt

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, standard_slip_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname":"inss_emp", "label":_("INSS Employee"), "fieldtype":"Currency", "width":130},
		{"fieldname":"inss_empr", "label":_("INSS Employer"), "fieldtype":"Currency", "width":130},
		{"fieldname":"family_allow", "label":_("Family Allowances"), "fieldtype":"Currency", "width":130},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ['INSS Pension Employee', 'INSS Pension Employer', 'INSS Family Allowances'])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		row["inss_emp"] = slip_amounts.get("INSS Pension Employee", 0)
		row["inss_empr"] = slip_amounts.get("INSS Pension Employer", 0)
		row["family_allow"] = slip_amounts.get("INSS Family Allowances", 0)
		del row["salary_slip"]

	return data
