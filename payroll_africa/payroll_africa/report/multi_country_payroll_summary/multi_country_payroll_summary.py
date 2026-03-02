import frappe
from frappe import _
from frappe.utils import flt


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
	conditions = get_conditions(filters)

	# Get salary slips with employee's payroll country
	salary_slips = frappe.db.sql(
		"""
		SELECT
			ss.name as salary_slip,
			COALESCE(e.payroll_country, c.country) as country,
			ss.gross_pay, ss.net_pay
		FROM `tabSalary Slip` ss
		LEFT JOIN `tabEmployee` e ON ss.employee = e.name
		LEFT JOIN `tabCompany` c ON ss.company = c.name
		WHERE ss.docstatus = 1 {conditions}
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	if not salary_slips:
		return []

	slip_names = [s.salary_slip for s in salary_slips]

	# Get deduction details for all slips
	details = frappe.db.sql(
		"""
		SELECT parent, amount, statistical_component
		FROM `tabSalary Detail`
		WHERE parent IN %s AND parentfield = 'deductions'
		""",
		(slip_names,),
		as_dict=True,
	)

	# Index details by parent
	slip_details = {}
	for d in details:
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


def get_conditions(filters):
	conditions = ""
	if filters.get("company_group"):
		lft, rgt = frappe.db.get_value("Company", filters["company_group"], ["lft", "rgt"])
		companies = frappe.db.sql_list(
			"SELECT name FROM `tabCompany` WHERE lft >= %s AND rgt <= %s",
			(lft, rgt),
		)
		conditions += " AND ss.company IN ({})".format(
			", ".join(frappe.db.escape(c) for c in companies)
		)
	elif filters.get("company"):
		conditions += " AND ss.company = %(company)s"
	if filters.get("from_date"):
		conditions += " AND ss.start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND ss.end_date <= %(to_date)s"
	return conditions
