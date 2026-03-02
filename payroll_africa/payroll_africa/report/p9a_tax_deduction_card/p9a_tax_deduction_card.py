import frappe
from frappe import _
from frappe.utils import flt, getdate

MONTHS = [
	"January", "February", "March", "April", "May", "June",
	"July", "August", "September", "October", "November", "December",
]


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
		{"fieldname": "basic_salary", "label": _("Basic Salary | A"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "benefits_non_cash", "label": _("Benefits NonCash | B"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "value_of_quarters", "label": _("Value of Quarters | C"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "total_gross_pay", "label": _("Total Gross Pay | D"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "e1_defined_contribution", "label": _("E1 (30% of A)"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "e2_defined_contribution", "label": _("E2 (NSSF)"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "e3_defined_contribution", "label": _("E3 (Other)"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "owner_occupied_interest", "label": _("Owner Occupied Interest | F"), "fieldtype": "Currency", "width": 160},
		{"fieldname": "retirement_and_owner_interest", "label": _("Retirement + Owner | G"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "chargeable_pay", "label": _("Chargeable Pay | H"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "tax_charged", "label": _("Tax Charged | I"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "personal_relief", "label": _("Personal Relief | K"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "insurance_relief", "label": _("Insurance Relief"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "paye_tax", "label": _("PAYE Tax | L"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "housing_levy", "label": _("Housing Levy | N"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "shif", "label": _("SHIF | J"), "fieldtype": "Currency", "width": 100},
	]


def get_data(filters):
	if not filters.get("employee") or not filters.get("fiscal_year"):
		return []

	fiscal_year = frappe.get_doc("Fiscal Year", filters["fiscal_year"])
	year_start = getdate(fiscal_year.year_start_date)
	year_end = getdate(fiscal_year.year_end_date)

	data = []
	for month_idx, month_name in enumerate(MONTHS):
		month_num = month_idx + 1
		# Build month start/end within fiscal year
		import calendar
		year = year_start.year if month_num >= year_start.month else year_start.year + 1
		last_day = calendar.monthrange(year, month_num)[1]
		month_start = getdate(f"{year}-{month_num:02d}-01")
		month_end = getdate(f"{year}-{month_num:02d}-{last_day}")

		# Skip months outside fiscal year
		if month_start > year_end or month_end < year_start:
			continue

		row = get_month_data(filters, month_name, month_start, month_end)
		data.append(row)

	return data


def get_month_data(filters, month_name, month_start, month_end):
	"""Get P9A data for a single month."""
	row = {"month": month_name}

	# Get salary slip for this employee/month
	salary_slip = frappe.db.sql(
		"""
		SELECT name, gross_pay
		FROM `tabSalary Slip`
		WHERE docstatus = 1
			AND employee = %(employee)s
			AND start_date >= %(month_start)s
			AND end_date <= %(month_end)s
			AND company = %(company)s
		LIMIT 1
		""",
		{
			"employee": filters["employee"],
			"month_start": month_start,
			"month_end": month_end,
			"company": filters["company"],
		},
		as_dict=True,
	)

	if not salary_slip:
		return row

	slip = salary_slip[0]

	# Get all p9a-tagged amounts from salary details
	p9a_amounts = get_p9a_amounts(slip.name)

	# Column A: Basic Salary
	basic = flt(p9a_amounts.get("Basic Salary", 0))
	row["basic_salary"] = basic

	# Column B: Benefits NonCash
	row["benefits_non_cash"] = flt(p9a_amounts.get("Benefits NonCash", 0))

	# Column C: Value of Quarters
	row["value_of_quarters"] = flt(p9a_amounts.get("Value of Quarters", 0))

	# Column D: Total Gross Pay (from salary slip)
	gross_pay = flt(slip.gross_pay)
	row["total_gross_pay"] = gross_pay

	# Column E1: 30% of basic salary
	e1 = flt(basic * 0.3)
	row["e1_defined_contribution"] = e1

	# Column E2: NSSF (Defined Contribution)
	e2 = flt(p9a_amounts.get("E2 Defined Contribution Retirement Scheme", 0))
	row["e2_defined_contribution"] = e2

	# Column E3: Other retirement contributions
	e3 = flt(p9a_amounts.get("E3 Defined Contribution Retirement Scheme", 0))
	row["e3_defined_contribution"] = e3

	# Column F: Owner Occupied Interest
	f_val = flt(p9a_amounts.get("Owner Occupied Interest", 0))
	row["owner_occupied_interest"] = f_val

	# Column G: min(E1, E2, E3) + F
	# Only consider non-zero E values for min calculation
	e_values = [v for v in [e1, e2, e3] if v > 0]
	min_e = min(e_values) if e_values else 0
	g_val = flt(min_e + f_val)
	row["retirement_and_owner_interest"] = g_val

	# Column H: Chargeable Pay (D - G)
	chargeable = p9a_amounts.get("Chargeable Pay")
	if chargeable is not None:
		row["chargeable_pay"] = flt(chargeable)
	else:
		row["chargeable_pay"] = flt(gross_pay - g_val)

	# Column I: Tax Charged
	row["tax_charged"] = flt(p9a_amounts.get("Tax Charged", 0))

	# Column K: Personal Relief
	row["personal_relief"] = flt(p9a_amounts.get("Personal Relief", 0))

	# Insurance Relief
	row["insurance_relief"] = flt(p9a_amounts.get("Insurance Relief", 0))

	# Column L: PAYE Tax
	row["paye_tax"] = flt(p9a_amounts.get("PAYE Tax", 0))

	# Column N: Housing Levy
	row["housing_levy"] = flt(p9a_amounts.get("Housing Levy", 0))

	# Column J: SHIF
	row["shif"] = flt(p9a_amounts.get("SHIF", 0))

	return row


def get_p9a_amounts(salary_slip_name):
	"""Get all p9a-tagged component amounts for a salary slip."""
	details = frappe.db.sql(
		"""
		SELECT sc.p9a_tax_deduction_card_type AS p9a_tag, sd.amount
		FROM `tabSalary Detail` sd
		INNER JOIN `tabSalary Component` sc ON sc.name = sd.salary_component
		WHERE sd.parent = %s
			AND sc.p9a_tax_deduction_card_type IS NOT NULL
			AND sc.p9a_tax_deduction_card_type != ''
		""",
		salary_slip_name,
		as_dict=True,
	)

	amounts = {}
	for d in details:
		tag = d.p9a_tag
		# Accumulate amounts for same tag (in case multiple components map to same tag)
		amounts[tag] = flt(amounts.get(tag, 0)) + flt(d.amount)

	return amounts
