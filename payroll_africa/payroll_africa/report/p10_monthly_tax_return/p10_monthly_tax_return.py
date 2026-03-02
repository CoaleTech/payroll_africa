import frappe
from frappe import _
from frappe.utils import flt

# P10A tag values that map to report columns
P10A_TAGS = [
	"Basic Salary",
	"Housing Allowance",
	"Transport Allowance",
	"Leave Pay",
	"Overtime",
	"Directors Fee",
	"Other Allowance",
	"Total Cash Pay",
	"Value of Car Benefit",
	"Other Non Cash Benefits",
	"Total Non Cash Pay",
	"Global Income",
	"Type of Housing",
	"Rent of House",
	"Computed Rent of House",
	"Rent Recovered from Employee",
	"Net Value of Housing",
	"Total Gross Pay",
	"30 Percent of Cash Pay",
	"Actual Contribution",
	"Permissible Limit",
	"Mortgage Interest",
	"Affordable Housing Levy",
	"SHIF",
	"Amount of Benefit",
	"Taxable Pay",
	"Tax Payable",
	"Monthly Personal Relief",
	"Amount of Insurance",
	"PAYE Tax",
	"Self Assessed PAYE Tax",
]


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{"fieldname": "tax_id", "label": _("Tax ID / PIN"), "fieldtype": "Data", "width": 120},
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 100},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
	]

	for tag in P10A_TAGS:
		fieldname = tag.lower().replace(" ", "_")
		columns.append({
			"fieldname": fieldname,
			"label": _(tag),
			"fieldtype": "Currency",
			"width": 120,
		})

	return columns


def get_data(filters):
	conditions = get_conditions(filters)

	# Get all salary slips matching filters, with p10a-tagged component amounts
	data = frappe.db.sql(
		"""
		SELECT
			e.tax_id,
			ss.employee,
			ss.employee_name,
			sc.p10a_tax_deduction_card_type AS p10a_tag,
			COALESCE(sd.amount, 0) AS amount
		FROM `tabSalary Slip` ss
		INNER JOIN `tabEmployee` e ON e.name = ss.employee
		INNER JOIN `tabSalary Detail` sd ON sd.parent = ss.name
		INNER JOIN `tabSalary Component` sc ON sc.name = sd.salary_component
		WHERE ss.docstatus = 1
			AND sc.p10a_tax_deduction_card_type IS NOT NULL
			AND sc.p10a_tax_deduction_card_type != ''
			{conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	# Pivot: one row per employee with p10a tags as columns
	employee_data = {}
	for row in data:
		key = row.employee
		if key not in employee_data:
			employee_data[key] = {
				"tax_id": row.tax_id or "",
				"employee": row.employee,
				"employee_name": row.employee_name,
			}

		tag = row.p10a_tag
		if tag:
			fieldname = tag.lower().replace(" ", "_")
			employee_data[key][fieldname] = flt(employee_data[key].get(fieldname, 0)) + flt(row.amount)

	return list(employee_data.values())


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND ss.company = %(company)s"
	if filters.get("employee"):
		conditions += " AND ss.employee = %(employee)s"
	if filters.get("from_date"):
		conditions += " AND ss.posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND ss.posting_date <= %(to_date)s"
	return conditions
