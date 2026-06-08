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
		{"fieldname": "ug_tin", "label": _("TIN"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Employment Income"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "nssf_employee", "label": _("NSSF Employee (5%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paye", "label": _("PAYE Tax"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay, ss.net_pay,
			e.ug_tin, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["NSSF Employee UG", "PAYE UG"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		nssf = slip_amounts.get("NSSF Employee UG", 0)
		row["nssf_employee"] = nssf
		row["taxable_income"] = flt(row.gross_pay) - nssf
		row["paye"] = slip_amounts.get("PAYE UG", 0)
		del row["salary_slip"]
		del row["net_pay"]

	return data
