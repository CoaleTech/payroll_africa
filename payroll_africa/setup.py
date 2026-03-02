import frappe
from frappe import _


def after_install():
	"""Run after app installation."""
	create_custom_fields()
	setup_kenya()
	setup_uganda()
	setup_tanzania()
	setup_rwanda()
	setup_burundi()
	setup_zambia()
	setup_malawi()
	setup_nigeria()
	setup_drc()
	setup_angola()
	setup_mozambique()
	setup_workspace_sidebar()
	setup_desktop_icon()


def after_migrate():
	"""Run after bench migrate."""
	create_custom_fields()
	setup_workspace_sidebar()
	setup_desktop_icon()


def create_custom_fields():
	"""Create custom fields on standard DocTypes."""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	p9a_options = (
		"\nBasic Salary\nBenefits NonCash\nValue of Quarters\nTotal Gross Pay"
		"\nE1 Defined Contribution Retirement Scheme"
		"\nE2 Defined Contribution Retirement Scheme"
		"\nE3 Defined Contribution Retirement Scheme"
		"\nOwner Occupied Interest"
		"\nRetirement Contribution and Owner Occupied Interest"
		"\nChargeable Pay\nHousing Levy\nSHIF\nTax Charged"
		"\nPersonal Relief\nInsurance Relief\nPAYE Tax"
	)
	p10a_options = (
		"\nBasic Salary\nHousing Allowance\nTransport Allowance"
		"\nLeave Pay\nOvertime\nDirectors Fee\nOther Allowance"
		"\nTotal Cash Pay\nValue of Car Benefit\nOther Non Cash Benefits"
		"\nTotal Non Cash Pay\nGlobal Income\nType of Housing"
		"\nRent of House\nComputed Rent of House"
		"\nRent Recovered from Employee\nNet Value of Housing"
		"\nTotal Gross Pay\n30 Percent of Cash Pay"
		"\nActual Contribution\nPermissible Limit\nMortgage Interest"
		"\nAffordable Housing Levy\nSHIF\nAmount of Benefit"
		"\nTaxable Pay\nTax Payable\nMonthly Personal Relief"
		"\nAmount of Insurance\nPAYE Tax\nSelf Assessed PAYE Tax"
	)

	custom_fields = {
		"Employee": [
			{
				"fieldname": "payroll_country",
				"fieldtype": "Link",
				"label": "Payroll Country",
				"options": "Country",
				"insert_after": "company",
				"description": "Country for statutory payroll deduction rules. Falls back to Company country if not set.",
				"module": "Payroll Africa",
			}
		],
		"Salary Component": [
			{
				"fieldname": "payroll_africa_section",
				"fieldtype": "Section Break",
				"label": "Kenya Statutory Tags",
				"insert_after": "description",
				"collapsible": 1,
				"module": "Payroll Africa",
			},
			{
				"fieldname": "p9a_tax_deduction_card_type",
				"fieldtype": "Select",
				"label": "P9A Tax Deduction Card Type",
				"options": p9a_options,
				"insert_after": "payroll_africa_section",
				"module": "Payroll Africa",
			},
			{
				"fieldname": "p10a_tax_deduction_card_type",
				"fieldtype": "Select",
				"label": "P10A Tax Deduction Card Type",
				"options": p10a_options,
				"insert_after": "p9a_tax_deduction_card_type",
				"module": "Payroll Africa",
			},
		],
	}
	create_custom_fields(custom_fields, update=True)


def _create_salary_structure(name, currency, deductions):
	"""Create a template Salary Structure for a country.

	Args:
		name: Salary Structure name, e.g. "Kenya Payroll Template"
		currency: Currency code, e.g. "KES"
		deductions: List of salary component names to add as deductions
	"""
	if frappe.db.exists("Salary Structure", name):
		return

	# Ensure Basic Salary component exists
	if not frappe.db.exists("Salary Component", "Basic Salary"):
		bs = frappe.new_doc("Salary Component")
		bs.salary_component = "Basic Salary"
		bs.salary_component_abbr = "BS"
		bs.type = "Earning"
		bs.is_tax_applicable = 1
		bs.flags.ignore_permissions = True
		bs.insert()

	doc = frappe.new_doc("Salary Structure")
	doc.__newname = name
	doc.is_active = "Yes"
	doc.payroll_frequency = "Monthly"
	doc.currency = currency

	# Basic Salary earning (formula = base)
	doc.append("earnings", {
		"salary_component": "Basic Salary",
		"amount_based_on_formula": 1,
		"formula": "base",
	})

	# All statutory deductions (amounts overridden by payroll hook)
	for component in deductions:
		doc.append("deductions", {
			"salary_component": component,
			"amount": 0,
		})

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_kenya():
	"""Set up Kenya payroll components, Income Tax Slab, and default settings."""
	_create_kenya_settings()
	_create_kenya_salary_components()
	_create_kenya_income_tax_slab()
	_create_salary_structure("Kenya Payroll Template", "KES", [
		"PAYE", "NSSF Employee", "NSSF Employer", "SHIF",
		"Housing Levy", "Employer Housing Levy", "NITA",
	])


def _create_kenya_settings():
	"""Create Kenya Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Kenya Payroll Settings"):
		return

	doc = frappe.new_doc("Kenya Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.personal_relief = 2400
	doc.insurance_relief_rate = 15
	doc.insurance_relief_cap = 5000
	doc.shif_rate = 2.75
	doc.shif_minimum = 300
	doc.ahl_employee_rate = 1.5
	doc.ahl_employer_rate = 1.5
	doc.nssf_tier1_rate = 6
	doc.nssf_tier1_cap = 1080
	doc.nssf_tier1_upper_limit = 18000
	doc.nssf_tier2_rate = 6
	doc.nssf_tier2_cap = 1080
	doc.nita_amount = 50

	# PAYE bands (monthly, KES)
	paye_bands = [
		{"from_amount": 0, "to_amount": 24000, "rate": 10},
		{"from_amount": 24001, "to_amount": 32333, "rate": 25},
		{"from_amount": 32334, "to_amount": 500000, "rate": 30},
		{"from_amount": 500001, "to_amount": 800000, "rate": 32.5},
		{"from_amount": 800001, "to_amount": 0, "rate": 35},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_kenya_salary_components():
	"""Create Kenya statutory salary components."""
	components = [
		{
			"salary_component": "PAYE",
			"salary_component_abbr": "PAYE",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "PAYE Tax",
			"p10a_tag": "PAYE Tax",
		},
		{
			"salary_component": "NSSF Employee",
			"salary_component_abbr": "NSSFe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "E2 Defined Contribution Retirement Scheme",
			"p10a_tag": "",
		},
		{
			"salary_component": "NSSF Employer",
			"salary_component_abbr": "NSSFr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "",
			"p10a_tag": "",
		},
		{
			"salary_component": "SHIF",
			"salary_component_abbr": "SHIF",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "SHIF",
			"p10a_tag": "SHIF",
		},
		{
			"salary_component": "Housing Levy",
			"salary_component_abbr": "AHL",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "Housing Levy",
			"p10a_tag": "Affordable Housing Levy",
		},
		{
			"salary_component": "Employer Housing Levy",
			"salary_component_abbr": "AHLr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "",
			"p10a_tag": "",
		},
		{
			"salary_component": "NITA",
			"salary_component_abbr": "NITA",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "",
			"p10a_tag": "",
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			# Update p9a/p10a tags on existing components
			if comp_data.get("p9a_tag") or comp_data.get("p10a_tag"):
				frappe.db.set_value("Salary Component", comp_name, {
					"p9a_tax_deduction_card_type": comp_data.get("p9a_tag", ""),
					"p10a_tax_deduction_card_type": comp_data.get("p10a_tag", ""),
				})
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		# Set p9a/p10a statutory tags
		if comp_data.get("p9a_tag"):
			doc.p9a_tax_deduction_card_type = comp_data["p9a_tag"]
		if comp_data.get("p10a_tag"):
			doc.p10a_tax_deduction_card_type = comp_data["p10a_tag"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_kenya_income_tax_slab():
	"""Create Kenya PAYE Income Tax Slab for 2025."""
	slab_name = "Kenya PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "KES"
	doc.allow_tax_exemption = 1

	# PAYE bands
	bands = [
		{"from_amount": 0, "to_amount": 24000, "percent_deduction": 10},
		{"from_amount": 24001, "to_amount": 32333, "percent_deduction": 25},
		{"from_amount": 32334, "to_amount": 500000, "percent_deduction": 30},
		{"from_amount": 500001, "to_amount": 800000, "percent_deduction": 32.5},
		{"from_amount": 800001, "to_amount": 0, "percent_deduction": 35},
	]
	for band in bands:
		doc.append("slabs", band)

	# Personal relief as negative tax
	doc.append("other_taxes_and_charges", {
		"description": "Personal Relief",
		"percent": 0,
		"min_taxable_income": 0,
		"max_taxable_income": 0,
		"flat_amount": -2400,
	})

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_uganda():
	"""Set up Uganda payroll components, Income Tax Slab, and default settings."""
	_create_uganda_settings()
	_create_uganda_salary_components()
	_create_uganda_income_tax_slab()
	_create_salary_structure("Uganda Payroll Template", "UGX", [
		"PAYE UG", "NSSF Employee UG", "NSSF Employer UG", "LST",
	])


def _create_uganda_settings():
	"""Create Uganda Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Uganda Payroll Settings"):
		return

	doc = frappe.new_doc("Uganda Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.nssf_employee_rate = 5
	doc.nssf_employer_rate = 10
	doc.lst_annual_amount = 100000

	# PAYE bands (monthly, UGX)
	paye_bands = [
		{"from_amount": 0, "to_amount": 235000, "rate": 0},
		{"from_amount": 235001, "to_amount": 335000, "rate": 10},
		{"from_amount": 335001, "to_amount": 410000, "rate": 20},
		{"from_amount": 410001, "to_amount": 10000000, "rate": 30},
		{"from_amount": 10000001, "to_amount": 0, "rate": 40},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_uganda_salary_components():
	"""Create Uganda statutory salary components."""
	components = [
		{
			"salary_component": "PAYE UG",
			"salary_component_abbr": "PAYEUG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NSSF Employee UG",
			"salary_component_abbr": "NSSFeUG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NSSF Employer UG",
			"salary_component_abbr": "NSSFrUG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "LST",
			"salary_component_abbr": "LST",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_uganda_income_tax_slab():
	"""Create Uganda PAYE Income Tax Slab for 2025."""
	slab_name = "Uganda PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "UGX"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, UGX)
	bands = [
		{"from_amount": 0, "to_amount": 235000, "percent_deduction": 0},
		{"from_amount": 235001, "to_amount": 335000, "percent_deduction": 10},
		{"from_amount": 335001, "to_amount": 410000, "percent_deduction": 20},
		{"from_amount": 410001, "to_amount": 10000000, "percent_deduction": 30},
		{"from_amount": 10000001, "to_amount": 0, "percent_deduction": 40},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_tanzania():
	"""Set up Tanzania payroll components, Income Tax Slab, and default settings."""
	_create_tanzania_settings()
	_create_tanzania_salary_components()
	_create_tanzania_income_tax_slab()
	_create_salary_structure("Tanzania Payroll Template", "TZS", [
		"PAYE TZ", "NSSF Employee TZ", "NSSF Employer TZ", "SDL", "WCF",
	])


def _create_tanzania_settings():
	"""Create Tanzania Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Tanzania Payroll Settings"):
		return

	doc = frappe.new_doc("Tanzania Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.nssf_employee_rate = 10
	doc.nssf_employer_rate = 10
	doc.sdl_rate = 3.5
	doc.wcf_rate = 0.5

	# PAYE bands (monthly, TZS)
	paye_bands = [
		{"from_amount": 0, "to_amount": 270000, "rate": 0},
		{"from_amount": 270001, "to_amount": 520000, "rate": 8},
		{"from_amount": 520001, "to_amount": 760000, "rate": 20},
		{"from_amount": 760001, "to_amount": 1000000, "rate": 25},
		{"from_amount": 1000001, "to_amount": 0, "rate": 30},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_tanzania_salary_components():
	"""Create Tanzania statutory salary components."""
	components = [
		{
			"salary_component": "PAYE TZ",
			"salary_component_abbr": "PAYETZ",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NSSF Employee TZ",
			"salary_component_abbr": "NSSFeTZ",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NSSF Employer TZ",
			"salary_component_abbr": "NSSFrTZ",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "SDL",
			"salary_component_abbr": "SDL",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "WCF",
			"salary_component_abbr": "WCF",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_tanzania_income_tax_slab():
	"""Create Tanzania PAYE Income Tax Slab for 2025."""
	slab_name = "Tanzania PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "TZS"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, TZS)
	bands = [
		{"from_amount": 0, "to_amount": 270000, "percent_deduction": 0},
		{"from_amount": 270001, "to_amount": 520000, "percent_deduction": 8},
		{"from_amount": 520001, "to_amount": 760000, "percent_deduction": 20},
		{"from_amount": 760001, "to_amount": 1000000, "percent_deduction": 25},
		{"from_amount": 1000001, "to_amount": 0, "percent_deduction": 30},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_rwanda():
	"""Set up Rwanda payroll components, Income Tax Slab, and default settings."""
	_create_rwanda_settings()
	_create_rwanda_salary_components()
	_create_rwanda_income_tax_slab()
	_create_salary_structure("Rwanda Payroll Template", "RWF", [
		"PAYE RW", "Pension Employee RW", "Pension Employer RW",
		"Maternity Employee RW", "Maternity Employer RW",
		"CBHI RW", "Occupational Hazards RW",
	])


def _create_rwanda_settings():
	"""Create Rwanda Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Rwanda Payroll Settings"):
		return

	doc = frappe.new_doc("Rwanda Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.pension_employee_rate = 6
	doc.pension_employer_rate = 6
	doc.maternity_employee_rate = 0.3
	doc.maternity_employer_rate = 0.3
	doc.cbhi_rate = 0.5
	doc.occupational_hazards_rate = 2

	# PAYE bands (monthly, RWF)
	paye_bands = [
		{"from_amount": 0, "to_amount": 60000, "rate": 0},
		{"from_amount": 60001, "to_amount": 100000, "rate": 10},
		{"from_amount": 100001, "to_amount": 200000, "rate": 20},
		{"from_amount": 200001, "to_amount": 0, "rate": 30},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_rwanda_salary_components():
	"""Create Rwanda statutory salary components."""
	components = [
		{
			"salary_component": "PAYE RW",
			"salary_component_abbr": "PAYERW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employee RW",
			"salary_component_abbr": "PENSeRW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employer RW",
			"salary_component_abbr": "PENSrRW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Maternity Employee RW",
			"salary_component_abbr": "MATeRW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Maternity Employer RW",
			"salary_component_abbr": "MATrRW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CBHI RW",
			"salary_component_abbr": "CBHIRW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Occupational Hazards RW",
			"salary_component_abbr": "OCCHRW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_rwanda_income_tax_slab():
	"""Create Rwanda PAYE Income Tax Slab for 2025."""
	slab_name = "Rwanda PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "RWF"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, RWF)
	bands = [
		{"from_amount": 0, "to_amount": 60000, "percent_deduction": 0},
		{"from_amount": 60001, "to_amount": 100000, "percent_deduction": 10},
		{"from_amount": 100001, "to_amount": 200000, "percent_deduction": 20},
		{"from_amount": 200001, "to_amount": 0, "percent_deduction": 30},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_burundi():
	"""Set up Burundi payroll components, Income Tax Slab, and default settings."""
	_create_burundi_settings()
	_create_burundi_salary_components()
	_create_burundi_income_tax_slab()
	_create_salary_structure("Burundi Payroll Template", "BIF", [
		"PAYE BI", "INSS Employee BI", "INSS Employer BI", "Work Injury BI",
		"Health Insurance Employee BI", "Health Insurance Employer BI",
		"Training Fund Employee BI", "Training Fund Employer BI",
	])


def _create_burundi_settings():
	"""Create Burundi Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Burundi Payroll Settings"):
		return

	doc = frappe.new_doc("Burundi Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_employee_rate = 4
	doc.inss_employer_rate = 6
	doc.work_injury_rate = 3
	doc.health_employee_rate = 3
	doc.health_employer_rate = 3
	doc.training_employee_rate = 1
	doc.training_employer_rate = 1

	# PAYE bands (monthly, BIF)
	paye_bands = [
		{"from_amount": 0, "to_amount": 150000, "rate": 0},
		{"from_amount": 150001, "to_amount": 300000, "rate": 20},
		{"from_amount": 300001, "to_amount": 600000, "rate": 25},
		{"from_amount": 600001, "to_amount": 0, "rate": 30},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_burundi_salary_components():
	"""Create Burundi statutory salary components."""
	components = [
		{
			"salary_component": "PAYE BI",
			"salary_component_abbr": "PAYEBI",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Employee BI",
			"salary_component_abbr": "INSSeBl",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Employer BI",
			"salary_component_abbr": "INSSrBI",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Work Injury BI",
			"salary_component_abbr": "WINJBI",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Health Insurance Employee BI",
			"salary_component_abbr": "HIeBI",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Health Insurance Employer BI",
			"salary_component_abbr": "HIrBI",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Training Fund Employee BI",
			"salary_component_abbr": "TFeBI",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Training Fund Employer BI",
			"salary_component_abbr": "TFrBI",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_burundi_income_tax_slab():
	"""Create Burundi PAYE Income Tax Slab for 2025."""
	slab_name = "Burundi PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "BIF"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, BIF)
	bands = [
		{"from_amount": 0, "to_amount": 150000, "percent_deduction": 0},
		{"from_amount": 150001, "to_amount": 300000, "percent_deduction": 20},
		{"from_amount": 300001, "to_amount": 600000, "percent_deduction": 25},
		{"from_amount": 600001, "to_amount": 0, "percent_deduction": 30},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_zambia():
	"""Set up Zambia payroll components, Income Tax Slab, and default settings."""
	_create_zambia_settings()
	_create_zambia_salary_components()
	_create_zambia_income_tax_slab()
	_create_salary_structure("Zambia Payroll Template", "ZMW", [
		"PAYE ZM", "NAPSA Employee ZM", "NAPSA Employer ZM",
		"NHIMA Employee ZM", "NHIMA Employer ZM",
	])


def _create_zambia_settings():
	"""Create Zambia Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Zambia Payroll Settings"):
		return

	doc = frappe.new_doc("Zambia Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.napsa_employee_rate = 5
	doc.napsa_employer_rate = 5
	doc.napsa_cap = 8541
	doc.nhima_employee_rate = 1
	doc.nhima_employer_rate = 1

	# PAYE bands (monthly, ZMW)
	paye_bands = [
		{"from_amount": 0, "to_amount": 5100, "rate": 0},
		{"from_amount": 5101, "to_amount": 7100, "rate": 20},
		{"from_amount": 7101, "to_amount": 9200, "rate": 30},
		{"from_amount": 9201, "to_amount": 0, "rate": 37},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_zambia_salary_components():
	"""Create Zambia statutory salary components."""
	components = [
		{
			"salary_component": "PAYE ZM",
			"salary_component_abbr": "PAYEZM",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NAPSA Employee ZM",
			"salary_component_abbr": "NAPSAeZM",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NAPSA Employer ZM",
			"salary_component_abbr": "NAPSArZM",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NHIMA Employee ZM",
			"salary_component_abbr": "NHIMAeZM",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NHIMA Employer ZM",
			"salary_component_abbr": "NHIMArZM",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_zambia_income_tax_slab():
	"""Create Zambia PAYE Income Tax Slab for 2025."""
	slab_name = "Zambia PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "ZMW"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, ZMW)
	bands = [
		{"from_amount": 0, "to_amount": 5100, "percent_deduction": 0},
		{"from_amount": 5101, "to_amount": 7100, "percent_deduction": 20},
		{"from_amount": 7101, "to_amount": 9200, "percent_deduction": 30},
		{"from_amount": 9201, "to_amount": 0, "percent_deduction": 37},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_malawi():
	"""Set up Malawi payroll components, Income Tax Slab, and default settings."""
	_create_malawi_settings()
	_create_malawi_salary_components()
	_create_malawi_income_tax_slab()
	_create_salary_structure("Malawi Payroll Template", "MWK", [
		"PAYE MW", "Pension Employee MW", "Pension Employer MW",
	])


def _create_malawi_settings():
	"""Create Malawi Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Malawi Payroll Settings"):
		return

	doc = frappe.new_doc("Malawi Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.pension_employee_rate = 5
	doc.pension_employer_rate = 10

	# PAYE bands (monthly, MWK)
	paye_bands = [
		{"from_amount": 0, "to_amount": 150000, "rate": 0},
		{"from_amount": 150001, "to_amount": 500000, "rate": 25},
		{"from_amount": 500001, "to_amount": 2550000, "rate": 30},
		{"from_amount": 2550001, "to_amount": 0, "rate": 35},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_malawi_salary_components():
	"""Create Malawi statutory salary components."""
	components = [
		{
			"salary_component": "PAYE MW",
			"salary_component_abbr": "PAYEMW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employee MW",
			"salary_component_abbr": "PENSeMW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employer MW",
			"salary_component_abbr": "PENSrMW",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_malawi_income_tax_slab():
	"""Create Malawi PAYE Income Tax Slab for 2025."""
	slab_name = "Malawi PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "MWK"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, MWK)
	bands = [
		{"from_amount": 0, "to_amount": 150000, "percent_deduction": 0},
		{"from_amount": 150001, "to_amount": 500000, "percent_deduction": 25},
		{"from_amount": 500001, "to_amount": 2550000, "percent_deduction": 30},
		{"from_amount": 2550001, "to_amount": 0, "percent_deduction": 35},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_drc():
	"""Set up DRC payroll components, Income Tax Slab, and default settings."""
	_create_drc_settings()
	_create_drc_salary_components()
	_create_drc_income_tax_slab()
	_create_salary_structure("DRC Payroll Template", "CDF", [
		"PAYE CD", "INSS Pension Employee CD", "INSS Pension Employer CD",
		"INSS Occupational Risks CD", "INSS Family Benefits CD",
		"INPP CD", "ONEM CD",
	])


def _create_drc_settings():
	"""Create DRC Payroll Settings with 2025 default rates."""
	if frappe.db.exists("DRC Payroll Settings"):
		return

	doc = frappe.new_doc("DRC Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_pension_employee_rate = 5
	doc.inss_pension_employer_rate = 5
	doc.inss_occupational_risks_rate = 1.5
	doc.inss_family_benefits_rate = 6.5
	doc.inpp_rate = 3
	doc.onem_rate = 0.2

	# PAYE/IPR bands (monthly, CDF)
	paye_bands = [
		{"from_amount": 0, "to_amount": 162000, "rate": 3},
		{"from_amount": 162001, "to_amount": 1800000, "rate": 15},
		{"from_amount": 1800001, "to_amount": 3600000, "rate": 30},
		{"from_amount": 3600001, "to_amount": 0, "rate": 40},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_drc_salary_components():
	"""Create DRC statutory salary components."""
	components = [
		{
			"salary_component": "PAYE CD",
			"salary_component_abbr": "PAYECD",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Pension Employee CD",
			"salary_component_abbr": "INSSeCD",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Pension Employer CD",
			"salary_component_abbr": "INSSrCD",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Occupational Risks CD",
			"salary_component_abbr": "INSSORCD",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Family Benefits CD",
			"salary_component_abbr": "INSSFBCD",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INPP CD",
			"salary_component_abbr": "INPPCD",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "ONEM CD",
			"salary_component_abbr": "ONEMCD",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_drc_income_tax_slab():
	"""Create DRC IPR/PAYE Income Tax Slab for 2025."""
	slab_name = "DRC PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "CDF"
	doc.allow_tax_exemption = 1

	# IPR/PAYE bands (monthly, CDF)
	bands = [
		{"from_amount": 0, "to_amount": 162000, "percent_deduction": 3},
		{"from_amount": 162001, "to_amount": 1800000, "percent_deduction": 15},
		{"from_amount": 1800001, "to_amount": 3600000, "percent_deduction": 30},
		{"from_amount": 3600001, "to_amount": 0, "percent_deduction": 40},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_nigeria():
	"""Set up Nigeria payroll components, Income Tax Slab, and default settings."""
	_create_nigeria_settings()
	_create_nigeria_salary_components()
	_create_nigeria_income_tax_slab()
	_create_salary_structure("Nigeria Payroll Template", "NGN", [
		"PAYE NG", "Pension Employee NG", "Pension Employer NG",
		"NHF NG", "NHIS Employee NG", "NHIS Employer NG",
		"NSITF NG", "ITF NG",
	])


def _create_nigeria_settings():
	"""Create Nigeria Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Nigeria Payroll Settings"):
		return

	doc = frappe.new_doc("Nigeria Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.pension_employee_rate = 8
	doc.pension_employer_rate = 10
	doc.nhf_rate = 2.5
	doc.nhis_employee_rate = 5
	doc.nhis_employer_rate = 10
	doc.nsitf_rate = 1
	doc.itf_rate = 1

	# PAYE bands (monthly, NGN)
	paye_bands = [
		{"from_amount": 0, "to_amount": 25000, "rate": 7},
		{"from_amount": 25001, "to_amount": 50000, "rate": 11},
		{"from_amount": 50001, "to_amount": 91667, "rate": 15},
		{"from_amount": 91668, "to_amount": 133333, "rate": 19},
		{"from_amount": 133334, "to_amount": 266667, "rate": 21},
		{"from_amount": 266668, "to_amount": 0, "rate": 24},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_nigeria_salary_components():
	"""Create Nigeria statutory salary components."""
	components = [
		{
			"salary_component": "PAYE NG",
			"salary_component_abbr": "PAYENG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employee NG",
			"salary_component_abbr": "PENSeNG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employer NG",
			"salary_component_abbr": "PENSrNG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NHF NG",
			"salary_component_abbr": "NHFNG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NHIS Employee NG",
			"salary_component_abbr": "NHISeNG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NHIS Employer NG",
			"salary_component_abbr": "NHISrNG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NSITF NG",
			"salary_component_abbr": "NSITFNG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "ITF NG",
			"salary_component_abbr": "ITFNG",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_nigeria_income_tax_slab():
	"""Create Nigeria PAYE Income Tax Slab for 2025."""
	slab_name = "Nigeria PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "NGN"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, NGN)
	bands = [
		{"from_amount": 0, "to_amount": 25000, "percent_deduction": 7},
		{"from_amount": 25001, "to_amount": 50000, "percent_deduction": 11},
		{"from_amount": 50001, "to_amount": 91667, "percent_deduction": 15},
		{"from_amount": 91668, "to_amount": 133333, "percent_deduction": 19},
		{"from_amount": 133334, "to_amount": 266667, "percent_deduction": 21},
		{"from_amount": 266668, "to_amount": 0, "percent_deduction": 24},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_mozambique():
	"""Set up Mozambique payroll components, Income Tax Slab, and default settings."""
	_create_mozambique_settings()
	_create_mozambique_salary_components()
	_create_mozambique_income_tax_slab()
	_create_salary_structure("Mozambique Payroll Template", "MZN", [
		"PAYE MZ", "INSS Employee MZ", "INSS Employer MZ",
	])


def _create_mozambique_settings():
	"""Create Mozambique Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Mozambique Payroll Settings"):
		return

	doc = frappe.new_doc("Mozambique Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_employee_rate = 3
	doc.inss_employer_rate = 4

	# PAYE bands (monthly, MZN)
	paye_bands = [
		{"from_amount": 0, "to_amount": 3500, "rate": 10},
		{"from_amount": 3501, "to_amount": 14000, "rate": 15},
		{"from_amount": 14001, "to_amount": 42000, "rate": 20},
		{"from_amount": 42001, "to_amount": 126000, "rate": 25},
		{"from_amount": 126001, "to_amount": 0, "rate": 32},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_mozambique_salary_components():
	"""Create Mozambique statutory salary components."""
	components = [
		{
			"salary_component": "PAYE MZ",
			"salary_component_abbr": "PAYEMZ",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Employee MZ",
			"salary_component_abbr": "INSSeMZ",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Employer MZ",
			"salary_component_abbr": "INSSrMZ",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_mozambique_income_tax_slab():
	"""Create Mozambique PAYE Income Tax Slab for 2025."""
	slab_name = "Mozambique PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "MZN"
	doc.allow_tax_exemption = 1

	# PAYE bands (monthly, MZN)
	bands = [
		{"from_amount": 0, "to_amount": 3500, "percent_deduction": 10},
		{"from_amount": 3501, "to_amount": 14000, "percent_deduction": 15},
		{"from_amount": 14001, "to_amount": 42000, "percent_deduction": 20},
		{"from_amount": 42001, "to_amount": 126000, "percent_deduction": 25},
		{"from_amount": 126001, "to_amount": 0, "percent_deduction": 32},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_angola():
	"""Set up Angola payroll components, Income Tax Slab, and default settings."""
	_create_angola_settings()
	_create_angola_salary_components()
	_create_angola_income_tax_slab()
	_create_salary_structure("Angola Payroll Template", "AOA", [
		"PAYE AO", "INSS Employee AO", "INSS Employer AO",
	])


def _create_angola_settings():
	"""Create Angola Payroll Settings with 2025 default rates."""
	if frappe.db.exists("Angola Payroll Settings"):
		return

	doc = frappe.new_doc("Angola Payroll Settings")
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_employee_rate = 3
	doc.inss_employer_rate = 8

	# PAYE/IRT bands (monthly, AOA)
	paye_bands = [
		{"from_amount": 0, "to_amount": 100000, "rate": 0},
		{"from_amount": 100001, "to_amount": 150000, "rate": 13},
		{"from_amount": 150001, "to_amount": 200000, "rate": 16},
		{"from_amount": 200001, "to_amount": 300000, "rate": 18},
		{"from_amount": 300001, "to_amount": 500000, "rate": 19},
		{"from_amount": 500001, "to_amount": 1000000, "rate": 20},
		{"from_amount": 1000001, "to_amount": 1500000, "rate": 21},
		{"from_amount": 1500001, "to_amount": 2000000, "rate": 22},
		{"from_amount": 2000001, "to_amount": 2500000, "rate": 23},
		{"from_amount": 2500001, "to_amount": 5000000, "rate": 24},
		{"from_amount": 5000001, "to_amount": 10000000, "rate": 24.5},
		{"from_amount": 10000001, "to_amount": 0, "rate": 25},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_angola_salary_components():
	"""Create Angola statutory salary components."""
	components = [
		{
			"salary_component": "PAYE AO",
			"salary_component_abbr": "PAYEAO",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Employee AO",
			"salary_component_abbr": "INSSeAO",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Employer AO",
			"salary_component_abbr": "INSSrAO",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		comp_name = comp_data["salary_component"]
		if frappe.db.exists("Salary Component", comp_name):
			continue

		doc = frappe.new_doc("Salary Component")
		doc.salary_component = comp_data["salary_component"]
		doc.salary_component_abbr = comp_data["salary_component_abbr"]
		doc.type = comp_data["type"]
		doc.variable_based_on_taxable_salary = comp_data["variable_based_on_taxable_salary"]
		doc.exempted_from_income_tax = comp_data["exempted_from_income_tax"]
		doc.statistical_component = comp_data["statistical_component"]
		doc.do_not_include_in_total = comp_data["do_not_include_in_total"]
		doc.remove_if_zero_valued = comp_data["remove_if_zero_valued"]
		doc.depends_on_payment_days = comp_data["depends_on_payment_days"]

		doc.flags.ignore_permissions = True
		doc.insert()


def _create_angola_income_tax_slab():
	"""Create Angola IRT/PAYE Income Tax Slab for 2025."""
	slab_name = "Angola PAYE 2025"
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""  # applicable to all companies
	doc.currency = "AOA"
	doc.allow_tax_exemption = 1

	# IRT/PAYE bands (monthly, AOA)
	bands = [
		{"from_amount": 0, "to_amount": 100000, "percent_deduction": 0},
		{"from_amount": 100001, "to_amount": 150000, "percent_deduction": 13},
		{"from_amount": 150001, "to_amount": 200000, "percent_deduction": 16},
		{"from_amount": 200001, "to_amount": 300000, "percent_deduction": 18},
		{"from_amount": 300001, "to_amount": 500000, "percent_deduction": 19},
		{"from_amount": 500001, "to_amount": 1000000, "percent_deduction": 20},
		{"from_amount": 1000001, "to_amount": 1500000, "percent_deduction": 21},
		{"from_amount": 1500001, "to_amount": 2000000, "percent_deduction": 22},
		{"from_amount": 2000001, "to_amount": 2500000, "percent_deduction": 23},
		{"from_amount": 2500001, "to_amount": 5000000, "percent_deduction": 24},
		{"from_amount": 5000001, "to_amount": 10000000, "percent_deduction": 24.5},
		{"from_amount": 10000001, "to_amount": 0, "percent_deduction": 25},
	]
	for band in bands:
		doc.append("slabs", band)

	doc.flags.ignore_permissions = True
	doc.insert()


def setup_workspace_sidebar():
	"""Payroll Africa has its own Workspace Sidebar via workspace_sidebar/payroll_africa.json.
	Remove any legacy items that were previously appended to the Payroll sidebar."""
	if not frappe.db.exists("Workspace Sidebar", "Payroll"):
		return

	sidebar = frappe.get_doc("Workspace Sidebar", "Payroll")

	# Remove any legacy Payroll Africa items from the Payroll sidebar
	legacy_labels = {
		"Payroll Africa", "Statutory Deductions Summary", "Employer Contributions",
		"Cost to Company", "P9A Tax Deduction Card", "P10 Monthly Tax Return",
		"NSSF Remittance", "SHIF Remittance", "Housing Levy Return",
		"Kenya Payroll Settings",
	}
	original_count = len(sidebar.items)
	sidebar.items = [item for item in sidebar.items if item.label not in legacy_labels]

	if len(sidebar.items) < original_count:
		sidebar.flags.ignore_permissions = True
		sidebar.save()
		frappe.db.commit()


def setup_desktop_icon():
	"""Create Desktop Icon for Payroll Africa under Frappe HR app."""
	if not frappe.db.exists("Desktop Icon", {"label": "Frappe HR", "icon_type": "App"}):
		return

	if frappe.db.exists("Desktop Icon", {"label": "Payroll Africa", "icon_type": "Link"}):
		# Update existing icon logo_url if needed
		existing = frappe.get_doc("Desktop Icon", {"label": "Payroll Africa", "icon_type": "Link"})
		if existing.logo_url != "/assets/payroll_africa/icons/desktop_icons/solid/payroll_africa.svg":
			existing.logo_url = "/assets/payroll_africa/icons/desktop_icons/solid/payroll_africa.svg"
			existing.flags.ignore_permissions = True
			existing.save()
			frappe.db.commit()
		return

	icon = frappe.new_doc("Desktop Icon")
	icon.label = "Payroll Africa"
	icon.app = "hrms"
	icon.icon = "globe"
	icon.icon_type = "Link"
	icon.link_to = "Payroll Africa"
	icon.link_type = "Workspace Sidebar"
	icon.logo_url = "/assets/payroll_africa/icons/desktop_icons/solid/payroll_africa.svg"
	icon.parent_icon = "Frappe HR"
	icon.standard = 1
	icon.flags.ignore_permissions = True
	icon.insert(ignore_if_duplicate=True)
	frappe.db.commit()


def before_uninstall():
	"""Clean up all data created by payroll_africa on uninstall."""
	_remove_desktop_icon()
	_remove_salary_structures()
	_remove_salary_components()
	_remove_income_tax_slabs()
	_remove_custom_fields()


def _remove_desktop_icon():
	"""Remove the Payroll Africa Desktop Icon."""
	name = frappe.db.get_value(
		"Desktop Icon", {"label": "Payroll Africa", "icon_type": "Link"}
	)
	if name:
		frappe.delete_doc("Desktop Icon", name, force=True)


def _remove_salary_structures():
	"""Remove template Salary Structures created by the app."""
	templates = [
		"Kenya Payroll Template", "Uganda Payroll Template",
		"Tanzania Payroll Template", "Rwanda Payroll Template",
		"Burundi Payroll Template", "Zambia Payroll Template",
		"Malawi Payroll Template", "DRC Payroll Template",
		"Nigeria Payroll Template", "Mozambique Payroll Template",
		"Angola Payroll Template",
	]
	for name in templates:
		if frappe.db.exists("Salary Structure", name):
			frappe.delete_doc("Salary Structure", name, force=True)


def _remove_salary_components():
	"""Remove statutory Salary Components created by the app."""
	components = [
		# Kenya
		"PAYE", "NSSF Employee", "NSSF Employer", "SHIF",
		"Housing Levy", "Employer Housing Levy", "NITA",
		# Uganda
		"PAYE UG", "NSSF Employee UG", "NSSF Employer UG", "LST",
		# Tanzania
		"PAYE TZ", "NSSF Employee TZ", "NSSF Employer TZ", "SDL", "WCF",
		# Rwanda
		"PAYE RW", "Pension Employee RW", "Pension Employer RW",
		"Maternity Employee RW", "Maternity Employer RW",
		"CBHI RW", "Occupational Hazards RW",
		# Burundi
		"PAYE BI", "INSS Employee BI", "INSS Employer BI", "Work Injury BI",
		"Health Insurance Employee BI", "Health Insurance Employer BI",
		"Training Fund Employee BI", "Training Fund Employer BI",
		# Zambia
		"PAYE ZM", "NAPSA Employee ZM", "NAPSA Employer ZM",
		"NHIMA Employee ZM", "NHIMA Employer ZM",
		# Malawi
		"PAYE MW", "Pension Employee MW", "Pension Employer MW",
		# DRC
		"PAYE CD", "INSS Pension Employee CD", "INSS Pension Employer CD",
		"INSS Occupational Risks CD", "INSS Family Benefits CD",
		"INPP CD", "ONEM CD",
		# Nigeria
		"PAYE NG", "Pension Employee NG", "Pension Employer NG",
		"NHF NG", "NHIS Employee NG", "NHIS Employer NG",
		"NSITF NG", "ITF NG",
		# Mozambique
		"PAYE MZ", "INSS Employee MZ", "INSS Employer MZ",
		# Angola
		"PAYE AO", "INSS Employee AO", "INSS Employer AO",
	]
	for name in components:
		if frappe.db.exists("Salary Component", name):
			frappe.delete_doc("Salary Component", name, force=True)


def _remove_income_tax_slabs():
	"""Remove Income Tax Slabs created by the app."""
	slabs = [
		"Kenya PAYE 2025", "Uganda PAYE 2025", "Tanzania PAYE 2025",
		"Rwanda PAYE 2025", "Burundi PAYE 2025", "Zambia PAYE 2025",
		"Malawi PAYE 2025", "DRC PAYE 2025", "Nigeria PAYE 2025",
		"Mozambique PAYE 2025", "Angola PAYE 2025",
	]
	for name in slabs:
		if frappe.db.exists("Income Tax Slab", name):
			frappe.delete_doc("Income Tax Slab", name, force=True)


def _remove_custom_fields():
	"""Remove custom fields added by the app."""
	fields = [
		"Employee-payroll_country",
		"Salary Component-payroll_africa_section",
		"Salary Component-p9a_tax_deduction_card_type",
		"Salary Component-p10a_tax_deduction_card_type",
	]
	for name in fields:
		if frappe.db.exists("Custom Field", name):
			frappe.delete_doc("Custom Field", name, force=True)
