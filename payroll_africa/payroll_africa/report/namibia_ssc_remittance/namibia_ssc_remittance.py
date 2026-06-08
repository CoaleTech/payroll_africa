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
		{"fieldname": "ssc_employee", "label": _("SSC Employee (0.9%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "ssc_employer", "label": _("SSC Employer (0.9%)"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "vet_levy", "label": _("VET Levy (1%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "ecf", "label": _("ECF"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "total_ssc", "label": _("Total SSC"), "fieldtype": "Currency", "width": 150},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name,
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
	amounts = fetch_component_amounts(slip_names, [
		"Social Security Employee", "Social Security Employer",
		"VET Levy", "Employees Compensation",
	])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("Social Security Employee", 0)
		empr = slip_amounts.get("Social Security Employer", 0)
		vet = slip_amounts.get("VET Levy", 0)
		ecf = slip_amounts.get("Employees Compensation", 0)
		row["ssc_employee"] = emp
		row["ssc_employer"] = empr
		row["vet_levy"] = vet
		row["ecf"] = ecf
		row["total_ssc"] = emp + empr + vet + ecf
		del row["salary_slip"]

	return data
