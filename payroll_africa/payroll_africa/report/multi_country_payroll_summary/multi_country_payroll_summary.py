import frappe
from frappe import _
from frappe.query_builder.functions import Coalesce
from frappe.utils import flt

from payroll_africa.payroll_africa.report.utils import deduction_details


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "country", "label": _("Country"), "fieldtype": "Data", "width": 150},
		{"fieldname": "employee_count", "label": _("Employee Count"), "fieldtype": "Int", "width": 130},
		{"fieldname": "total_gross", "label": _("Total Gross Pay"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "total_employee_deductions", "label": _("Total Employee Deductions"), "fieldtype": "Currency", "width": 180},
		{"fieldname": "total_employer_contributions", "label": _("Total Employer Contributions"), "fieldtype": "Currency", "width": 190},
		{"fieldname": "total_net_pay", "label": _("Total Net Pay"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "cost_to_company", "label": _("Cost to Company"), "fieldtype": "Currency", "width": 150},
	]


def get_data(filters):
	ss = frappe.qb.DocType("Salary Slip")
	emp = frappe.qb.DocType("Employee")
	company = frappe.qb.DocType("Company")
	# Salary slips with the employee's payroll country, falling back to the company's
	query = (
		frappe.qb.from_(ss)
		.left_join(emp)
		.on(ss.employee == emp.name)
		.left_join(company)
		.on(ss.company == company.name)
		.select(ss.name.as_("salary_slip"), Coalesce(emp.payroll_country, company.country).as_("country"), ss.gross_pay, ss.net_pay)
		.where(ss.docstatus == 1)
	)
	if filters.get("company_group"):
		lft, rgt = frappe.db.get_value("Company", filters["company_group"], ["lft", "rgt"])
		companies = frappe.get_all("Company", filters=[["lft", ">=", lft], ["rgt", "<=", rgt]], pluck="name")
		if companies:
			query = query.where(ss.company.isin(companies))
	elif filters.get("company"):
		query = query.where(ss.company == filters["company"])
	if filters.get("from_date"):
		query = query.where(ss.start_date >= filters["from_date"])
	if filters.get("to_date"):
		query = query.where(ss.end_date <= filters["to_date"])
	salary_slips = query.run(as_dict=True)

	if not salary_slips:
		return []

	slip_names = [s.salary_slip for s in salary_slips]

	slip_details = {}
	for d in deduction_details(slip_names):
		slip_details.setdefault(d.parent, []).append(d)

	# Aggregate by country
	country_data = {}
	for slip in salary_slips:
		country = slip.country or "Unknown"
		if country not in country_data:
			country_data[country] = {
				"country": country,
				"employee_count": 0,
				"total_gross": 0,
				"total_employee_deductions": 0,
				"total_employer_contributions": 0,
				"total_net_pay": 0,
			}

		row = country_data[country]
		row["employee_count"] += 1
		row["total_gross"] += flt(slip.gross_pay)
		row["total_net_pay"] += flt(slip.net_pay)

		for detail in slip_details.get(slip.salary_slip, []):
			if detail.statistical_component:
				row["total_employer_contributions"] += flt(detail.amount)
			else:
				row["total_employee_deductions"] += flt(detail.amount)

	# Compute cost to company and build result
	data = []
	for country in sorted(country_data.keys()):
		row = country_data[country]
		row["cost_to_company"] = row["total_gross"] + row["total_employer_contributions"]
		data.append(row)

	return data
