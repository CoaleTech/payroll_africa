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
		{"fieldname": "cd_national_id", "label": _("National ID"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "inss_employee", "label": _("INSS Employee (5%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "prof_expenses", "label": _("Prof. Expenses (20%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "taxable_remuneration", "label": _("Taxable Remuneration"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "ipr_tax", "label": _("IPR Tax"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "inss_employer", "label": _("INSS Employer (5%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "inss_occ_risks", "label": _("Occ. Risks (1.5%)"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "inss_family", "label": _("Family Benefits (6.5%)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "inpp", "label": _("INPP (1%)"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "onem", "label": _("ONEM (0.2%)"), "fieldtype": "Currency", "width": 110},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.cd_national_id, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	component_map = {
		"INSS Pension Employee CD": "inss_employee",
		"INSS Pension Employer CD": "inss_employer",
		"INSS Occupational Risks CD": "inss_occ_risks",
		"INSS Family Benefits CD": "inss_family",
		"INPP CD": "inpp",
		"ONEM CD": "onem",
		"PAYE CD": "ipr_tax",
	}

	for row in data:
		slip = row.salary_slip

		for comp_name, field in component_map.items():
			amount = flt(frappe.db.get_value(
				"Salary Detail",
				{"parent": slip, "salary_component": comp_name, "parentfield": "deductions"},
				"amount",
			))
			row[field] = amount

		inss_emp = flt(row.get("inss_employee", 0))
		after_inss = flt(row.gross_pay) - inss_emp
		row["prof_expenses"] = flt(after_inss * 0.2)
		row["taxable_remuneration"] = after_inss - row["prof_expenses"]
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
