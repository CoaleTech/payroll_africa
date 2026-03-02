import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "tz_tin", "label": _("TIN"), "fieldtype": "Data", "width": 120},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "nssf_employee", "label": _("NSSF Employee (10%)"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "taxable_income", "label": _("Taxable Income"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paye", "label": _("PAYE"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "sdl", "label": _("SDL (3.5%)"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "wcf", "label": _("WCF (0.5%)"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay,
			e.tz_tin, ss.name as salary_slip
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	for row in data:
		slip = row.salary_slip
		components = {"NSSF Employee TZ": 0, "PAYE TZ": 0, "SDL": 0, "WCF": 0}
		for comp_name in components:
			components[comp_name] = flt(frappe.db.get_value(
				"Salary Detail",
				{"parent": slip, "salary_component": comp_name, "parentfield": "deductions"},
				"amount",
			))

		row["nssf_employee"] = components["NSSF Employee TZ"]
		row["taxable_income"] = flt(row.gross_pay) - components["NSSF Employee TZ"]
		row["paye"] = components["PAYE TZ"]
		row["sdl"] = components["SDL"]
		row["wcf"] = components["WCF"]
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
