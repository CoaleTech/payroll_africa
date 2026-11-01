import frappe
from frappe import _


from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, standard_slip_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	emp_rate = frappe.db.get_value("Tunisia Payroll Settings", None, "cnss_employee_rate") or 9.68
	empr_rate = frappe.db.get_value("Tunisia Payroll Settings", None, "cnss_employer_rate") or 17.07
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "cnss_employee", "label": _("CNSS Employee ({0}%)").format(emp_rate), "fieldtype": "Currency", "width": 180},
		{"fieldname": "cnss_employer", "label": _("CNSS Employer ({0}%)").format(empr_rate), "fieldtype": "Currency", "width": 180},
		{"fieldname": "ssc", "label": _("Social Solidarity Contribution (0.5%)"), "fieldtype": "Currency", "width": 220},
		{"fieldname": "total_cnss", "label": _("Total CNSS"), "fieldtype": "Currency", "width": 150},
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
	amounts = fetch_component_amounts(slip_names, ["CNSS Employee", "CNSS Employer", "Social Solidarity Contribution"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		emp = slip_amounts.get("CNSS Employee", 0)
		empr = slip_amounts.get("CNSS Employer", 0)
		ssc = slip_amounts.get("Social Solidarity Contribution", 0)
		row["cnss_employee"] = emp
		row["cnss_employer"] = empr
		row["ssc"] = ssc
		row["total_cnss"] = emp + empr + ssc
		del row["salary_slip"]

	return data
