import frappe
from frappe import _
from frappe.utils import flt, formatdate

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, standard_slip_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "cnapps_employee", "label": _("CNaPS Employee"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "cnapps_employer", "label": _("CNaPS Employer"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "health_insurance_employee", "label": _("Health Insurance Employee"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "health_insurance_employer", "label": _("Health Insurance Employer"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "fmfp_training_fund", "label": _("FMFP Training Fund"), "fieldtype": "Currency", "width": 160},
		{"fieldname": "total_cnapps", "label": _("Total CNaPS"), "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	conditions = standard_slip_conditions(filters)

	data = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay, ss.start_date,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		WHERE ss.docstatus = 1"""
		+ conditions
		+ """
		ORDER BY ss.employee, ss.start_date
		""",
		filters,
		as_dict=True,
	)

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(
		slip_names,
		["CNaPS Employee", "CNaPS Employer", "Health Insurance Employee", "Health Insurance Employer", "FMFP Training Fund"],
	)

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		ce = slip_amounts.get("CNaPS Employee", 0)
		cr = slip_amounts.get("CNaPS Employer", 0)
		hie = slip_amounts.get("Health Insurance Employee", 0)
		hir = slip_amounts.get("Health Insurance Employer", 0)
		fmfp = slip_amounts.get("FMFP Training Fund", 0)
		row["cnapps_employee"] = ce
		row["cnapps_employer"] = cr
		row["health_insurance_employee"] = hie
		row["health_insurance_employer"] = hir
		row["fmfp_training_fund"] = fmfp
		row["total_cnapps"] = ce + cr + hie + hir + fmfp
		row["month"] = formatdate(row.start_date, "MMM-YYYY")
		del row["salary_slip"]
		del row["start_date"]

	return data
