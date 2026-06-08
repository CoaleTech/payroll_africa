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
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 100},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 160},
		{"fieldname": "rw_tin", "label": _("TIN"), "fieldtype": "Data", "width": 110},
		{"fieldname": "rw_ssn", "label": _("SSN"), "fieldtype": "Data", "width": 110},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "pension_employee", "label": _("Pension Emp (6%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "pension_employer", "label": _("Pension Er (6%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "maternity_employee", "label": _("Maternity Emp (0.3%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "maternity_employer", "label": _("Maternity Er (0.3%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "cbhi", "label": _("CBHI (0.5%)"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "occupational_hazards", "label": _("Occ. Hazards (2%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "total_rssb", "label": _("Total RSSB"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.rw_tin, e.rw_ssn, ss.name as salary_slip
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

	component_map = {
		"Pension Employee RW": "pension_employee",
		"Pension Employer RW": "pension_employer",
		"Maternity Employee RW": "maternity_employee",
		"Maternity Employer RW": "maternity_employer",
		"CBHI RW": "cbhi",
		"Occupational Hazards RW": "occupational_hazards",
		"PAYE RW": "paye",
	}

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, list(component_map.keys()))

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		total_rssb = 0

		for comp_name, field in component_map.items():
			amount = slip_amounts.get(comp_name, 0)
			row[field] = amount
			if field != "paye":
				total_rssb += amount

		row["taxable_income"] = flt(row.gross_pay) - flt(row.get("pension_employee", 0))
		row["total_rssb"] = total_rssb
		del row["salary_slip"]

	return data
