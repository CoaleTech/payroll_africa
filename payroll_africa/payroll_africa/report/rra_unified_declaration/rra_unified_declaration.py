import frappe
from frappe import _
from frappe.utils import flt


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
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.rw_tin, e.rw_ssn, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
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

	for row in data:
		slip = row.salary_slip
		total_rssb = 0

		for comp_name, field in component_map.items():
			amount = flt(frappe.db.get_value(
				"Salary Detail",
				{"parent": slip, "salary_component": comp_name, "parentfield": "deductions"},
				"amount",
			))
			row[field] = amount
			if field != "paye":
				total_rssb += amount

		row["taxable_income"] = flt(row.gross_pay) - flt(row.get("pension_employee", 0))
		row["total_rssb"] = total_rssb
		del row["salary_slip"]

	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND ss.company = %(company)s"
	if filters.get("from_date"):
		conditions += " AND ss.start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND ss.end_date <= %(to_date)s"
	return conditions
