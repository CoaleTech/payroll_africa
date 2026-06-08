import frappe


# ── Currency codes required by each country setup ──────────────────────
REQUIRED_CURRENCIES = {
	"KES": {"currency_name": "Kenyan Shilling", "symbol": "KSh", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"UGX": {"currency_name": "Ugandan Shilling", "symbol": "USh", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Cent", "fraction_units": 100},
	"TZS": {"currency_name": "Tanzanian Shilling", "symbol": "TSh", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Cent", "fraction_units": 100},
	"RWF": {"currency_name": "Rwandan Franc", "symbol": "FRw", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Centime", "fraction_units": 100},
	"BIF": {"currency_name": "Burundian Franc", "symbol": "FBu", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Centime", "fraction_units": 100},
	"ZMW": {"currency_name": "Zambian Kwacha", "symbol": "ZK", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Ngwee", "fraction_units": 100},
	"MWK": {"currency_name": "Malawian Kwacha", "symbol": "MK", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Tambala", "fraction_units": 100},
	"CDF": {"currency_name": "Congolese Franc", "symbol": "FC", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Centime", "fraction_units": 100},
	"NGN": {"currency_name": "Nigerian Naira", "symbol": "₦", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Kobo", "fraction_units": 100},
	"MZN": {"currency_name": "Mozambican Metical", "symbol": "MT", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Centavo", "fraction_units": 100},
	"AOA": {"currency_name": "Angolan Kwanza", "symbol": "Kz", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cêntimo", "fraction_units": 100},
	"ETB": {"currency_name": "Ethiopian Birr", "symbol": "Br", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Santim", "fraction_units": 100},
	"ZAR": {"currency_name": "South African Rand", "symbol": "R", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"EGP": {"currency_name": "Egyptian Pound", "symbol": "£", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Piastre", "fraction_units": 100},
	"GHS": {"currency_name": "Ghanaian Cedi", "symbol": "GH₵", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Pesewa", "fraction_units": 100},
	"BWP": {"currency_name": "Botswana Pula", "symbol": "P", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Thebe", "fraction_units": 100},
	"MAD": {"currency_name": "Moroccan Dirham", "symbol": "DH", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Centime", "fraction_units": 100},
	"XOF": {"currency_name": "West African CFA Franc", "symbol": "CFA", "number_format": "# ###.##", "smallest_currency_fraction_value": 1, "fraction": "Centime", "fraction_units": 100},
	"TND": {"currency_name": "Tunisian Dinar", "symbol": "DT", "number_format": "# ###.###", "smallest_currency_fraction_value": 0.001, "fraction": "Millime", "fraction_units": 1000},
	"NAD": {"currency_name": "Namibian Dollar", "symbol": "N$", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"MGA": {"currency_name": "Malagasy Ariary", "symbol": "Ar", "number_format": "# ###.##", "smallest_currency_fraction_value": 1, "fraction": "Iraimbilanja", "fraction_units": 5},
}


def _ensure_currencies():
	"""Create Currency records that don't already exist.

	ERPNext ships many currencies but a fresh installation may be missing some
	African currencies (e.g. AOA, MZN, CDF).  This helper guarantees every
	currency referenced by the country setups is present before we try to link
	to it.
	"""
	# Currency is autonamed by `currency_name` (the record's primary key equals
	# its currency_name).  Every country setup links currencies by ISO code, so
	# each Currency must be named by code.  We therefore set currency_name = code
	# and heal any record a previous run created under the full descriptive name.
	for code, meta in REQUIRED_CURRENCIES.items():
		full_name = meta["currency_name"]
		if not frappe.db.exists("Currency", code) and full_name != code \
				and frappe.db.exists("Currency", full_name):
			frappe.rename_doc("Currency", full_name, code, force=True)
			frappe.db.set_value("Currency", code, "currency_name", code)

		if frappe.db.exists("Currency", code):
			continue

		doc = frappe.new_doc("Currency")
		doc.currency_name = code  # autoname -> primary key == ISO code
		doc.symbol = meta.get("symbol", "")
		doc.number_format = meta.get("number_format", "#,###.##")
		doc.smallest_currency_fraction_value = meta.get("smallest_currency_fraction_value", 0.01)
		doc.fraction = meta.get("fraction", "")
		doc.fraction_units = meta.get("fraction_units", 100)
		doc.enabled = 1
		doc.flags.ignore_permissions = True
		doc.insert(ignore_if_duplicate=True)


def _setup_custom_fields():
	"""Create or update custom fields added by this app."""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
	create_custom_fields({
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
				"options": "\nBasic Salary\nBenefits NonCash\nValue of Quarters\nTotal Gross Pay\nE1 Defined Contribution Retirement Scheme\nE2 Defined Contribution Retirement Scheme\nE3 Defined Contribution Retirement Scheme\nOwner Occupied Interest\nRetirement Contribution and Owner Occupied Interest\nChargeable Pay\nHousing Levy\nSHIF\nTax Charged\nPersonal Relief\nInsurance Relief\nPAYE Tax",
				"insert_after": "payroll_africa_section",
				"module": "Payroll Africa",
			},
			{
				"fieldname": "p10a_tax_deduction_card_type",
				"fieldtype": "Select",
				"label": "P10A Tax Deduction Card Type",
				"options": "\nBasic Salary\nHousing Allowance\nTransport Allowance\nLeave Pay\nOvertime\nDirectors Fee\nOther Allowance\nTotal Cash Pay\nValue of Car Benefit\nOther Non Cash Benefits\nTotal Non Cash Pay\nGlobal Income\nType of Housing\nRent of House\nComputed Rent of House\nRent Recovered from Employee\nNet Value of Housing\nTotal Gross Pay\n30 Percent of Cash Pay\nActual Contribution\nPermissible Limit\nMortgage Interest\nAffordable Housing Levy\nSHIF\nAmount of Benefit\nTaxable Pay\nTax Payable\nMonthly Personal Relief\nAmount of Insurance\nPAYE Tax\nSelf Assessed PAYE Tax",
				"insert_after": "p9a_tax_deduction_card_type",
				"module": "Payroll Africa",
			},
		],
	})


def _upsert_salary_component(comp_data: dict):
	"""Insert a Salary Component or update its p9a/p10a tags if it already exists."""
	name = comp_data["salary_component"]
	if frappe.db.exists("Salary Component", name):
		updates = {}
		for tag_field in ("p9a_tax_deduction_card_type", "p10a_tax_deduction_card_type"):
			tag_key = tag_field.replace("_tax_deduction_card_type", "_tag")
			if comp_data.get(tag_key):
				updates[tag_field] = comp_data[tag_key]
		if updates:
			frappe.db.set_value("Salary Component", name, updates)
		return

	doc = frappe.new_doc("Salary Component")
	for field in ("salary_component", "salary_component_abbr", "type",
				  "variable_based_on_taxable_salary", "exempted_from_income_tax",
				  "statistical_component", "do_not_include_in_total",
				  "remove_if_zero_valued", "depends_on_payment_days"):
		setattr(doc, field, comp_data.get(field, 0))
	if comp_data.get("p9a_tag"):
		doc.p9a_tax_deduction_card_type = comp_data["p9a_tag"]
	if comp_data.get("p10a_tag"):
		doc.p10a_tax_deduction_card_type = comp_data["p10a_tag"]
	doc.flags.ignore_permissions = True
	doc.insert()


def _create_income_tax_slab(slab_name: str, currency: str, bands: list, personal_relief: float = 0):
	"""Create an Income Tax Slab unless one with this name already exists."""
	if frappe.db.exists("Income Tax Slab", slab_name):
		return

	doc = frappe.new_doc("Income Tax Slab")
	doc.__newname = slab_name
	doc.effective_from = "2025-01-01"
	doc.company = ""
	doc.currency = currency
	doc.allow_tax_exemption = 1

	for band in bands:
		doc.append("slabs", {
			"from_amount": band["from_amount"],
			"to_amount": band["to_amount"],
			"percent_deduction": band["rate"],
		})

	if personal_relief:
		doc.append("other_taxes_and_charges", {
			"description": "Personal Relief",
			"percent": 0,
			"flat_amount": -personal_relief,
		})

	doc.flags.ignore_permissions = True
	doc.insert()


def _run_setup():
	"""Shared setup logic for install and migrate."""
	_ensure_currencies()
	_setup_custom_fields()
	for setup_fn in (
		setup_kenya, setup_uganda, setup_tanzania, setup_rwanda,
		setup_burundi, setup_zambia, setup_malawi, setup_nigeria,
		setup_drc, setup_angola, setup_mozambique,
		setup_ethiopia, setup_south_africa, setup_egypt, setup_ghana,
		setup_botswana, setup_morocco, setup_tunisia, setup_namibia,
		setup_madagascar, setup_ivory_coast,
	):
		setup_fn()
	setup_workspace_sidebar()
	setup_desktop_icon()


def after_install():
	"""Run after app installation."""
	_run_setup()


def after_migrate():
	"""Run after bench migrate."""
	_run_setup()


def _create_salary_structure(name, currency, deductions):
	"""Create a template Salary Structure for a country.

	Args:
		name: Salary Structure name, e.g. "Kenya Payroll Template"
		currency: Currency code, e.g. "KES"
		deductions: List of salary component names to add as deductions
	"""
	if frappe.db.exists("Salary Structure", name):
		return

	if not frappe.db.exists("Salary Component", "Basic Salary"):
		bs = frappe.new_doc("Salary Component")
		bs.salary_component = "Basic Salary"
		bs.salary_component_abbr = "BS"
		bs.type = "Earning"
		bs.is_tax_applicable = 1
		bs.flags.ignore_permissions = True
		bs.insert()

	company = frappe.db.get_default("company") or frappe.db.get_value("Company", {}, "name")
	if not company:
		return

	doc = frappe.new_doc("Salary Structure")
	doc.__newname = name
	doc.is_active = "Yes"
	doc.payroll_frequency = "Monthly"
	doc.currency = currency
	doc.company = company

	doc.append("earnings", {
		"salary_component": "Basic Salary",
		"amount_based_on_formula": 1,
		"formula": "base",
	})

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
	doc = frappe.get_doc("Kenya Payroll Settings")
	if doc.paye_bands:
		return
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
		_upsert_salary_component(comp_data)


def _create_kenya_income_tax_slab():
	"""Create Kenya PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Kenya PAYE 2025",
		currency="KES",
		bands=[
			{"from_amount": 0, "to_amount": 24000, "rate": 10},
			{"from_amount": 24001, "to_amount": 32333, "rate": 25},
			{"from_amount": 32334, "to_amount": 500000, "rate": 30},
			{"from_amount": 500001, "to_amount": 800000, "rate": 32.5},
			{"from_amount": 800001, "to_amount": 0, "rate": 35},
		],
		personal_relief=2400,
	)


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
	doc = frappe.get_doc("Uganda Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.nssf_employee_rate = 5
	doc.nssf_employer_rate = 10
	doc.lst_annual_amount = 100000

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
		_upsert_salary_component(comp_data)


def _create_uganda_income_tax_slab():
	"""Create Uganda PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Uganda PAYE 2025",
		currency="UGX",
		bands=[
			{"from_amount": 0, "to_amount": 235000, "rate": 0},
			{"from_amount": 235001, "to_amount": 335000, "rate": 10},
			{"from_amount": 335001, "to_amount": 410000, "rate": 20},
			{"from_amount": 410001, "to_amount": 10000000, "rate": 30},
			{"from_amount": 10000001, "to_amount": 0, "rate": 40},
		],
	)


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
	doc = frappe.get_doc("Tanzania Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.nssf_employee_rate = 10
	doc.nssf_employer_rate = 10
	doc.sdl_rate = 3.5
	doc.wcf_rate = 0.5

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
		_upsert_salary_component(comp_data)


def _create_tanzania_income_tax_slab():
	"""Create Tanzania PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Tanzania PAYE 2025",
		currency="TZS",
		bands=[
			{"from_amount": 0, "to_amount": 270000, "rate": 0},
			{"from_amount": 270001, "to_amount": 520000, "rate": 8},
			{"from_amount": 520001, "to_amount": 760000, "rate": 20},
			{"from_amount": 760001, "to_amount": 1000000, "rate": 25},
			{"from_amount": 1000001, "to_amount": 0, "rate": 30},
		],
	)


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
	doc = frappe.get_doc("Rwanda Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.pension_employee_rate = 6
	doc.pension_employer_rate = 6
	doc.maternity_employee_rate = 0.3
	doc.maternity_employer_rate = 0.3
	doc.cbhi_rate = 0.5
	doc.occupational_hazards_rate = 2

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
		_upsert_salary_component(comp_data)


def _create_rwanda_income_tax_slab():
	"""Create Rwanda PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Rwanda PAYE 2025",
		currency="RWF",
		bands=[
			{"from_amount": 0, "to_amount": 60000, "rate": 0},
			{"from_amount": 60001, "to_amount": 100000, "rate": 10},
			{"from_amount": 100001, "to_amount": 200000, "rate": 20},
			{"from_amount": 200001, "to_amount": 0, "rate": 30},
		],
	)


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
	doc = frappe.get_doc("Burundi Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_employee_rate = 4
	doc.inss_employer_rate = 6
	doc.work_injury_rate = 3
	doc.health_employee_rate = 3
	doc.health_employer_rate = 3
	doc.training_employee_rate = 1
	doc.training_employer_rate = 1

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
		_upsert_salary_component(comp_data)


def _create_burundi_income_tax_slab():
	"""Create Burundi PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Burundi PAYE 2025",
		currency="BIF",
		bands=[
			{"from_amount": 0, "to_amount": 150000, "rate": 0},
			{"from_amount": 150001, "to_amount": 300000, "rate": 20},
			{"from_amount": 300001, "to_amount": 600000, "rate": 25},
			{"from_amount": 600001, "to_amount": 0, "rate": 30},
		],
	)


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
	doc = frappe.get_doc("Zambia Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.napsa_employee_rate = 5
	doc.napsa_employer_rate = 5
	doc.napsa_cap = 8541
	doc.nhima_employee_rate = 1
	doc.nhima_employer_rate = 1

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
		_upsert_salary_component(comp_data)


def _create_zambia_income_tax_slab():
	"""Create Zambia PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Zambia PAYE 2025",
		currency="ZMW",
		bands=[
			{"from_amount": 0, "to_amount": 5100, "rate": 0},
			{"from_amount": 5101, "to_amount": 7100, "rate": 20},
			{"from_amount": 7101, "to_amount": 9200, "rate": 30},
			{"from_amount": 9201, "to_amount": 0, "rate": 37},
		],
	)


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
	doc = frappe.get_doc("Malawi Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.pension_employee_rate = 5
	doc.pension_employer_rate = 10

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
		_upsert_salary_component(comp_data)


def _create_malawi_income_tax_slab():
	"""Create Malawi PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Malawi PAYE 2025",
		currency="MWK",
		bands=[
			{"from_amount": 0, "to_amount": 150000, "rate": 0},
			{"from_amount": 150001, "to_amount": 500000, "rate": 25},
			{"from_amount": 500001, "to_amount": 2550000, "rate": 30},
			{"from_amount": 2550001, "to_amount": 0, "rate": 35},
		],
	)


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
	doc = frappe.get_doc("DRC Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_pension_employee_rate = 5
	doc.inss_pension_employer_rate = 5
	doc.inss_occupational_risks_rate = 1.5
	doc.inss_family_benefits_rate = 6.5
	doc.inpp_rate = 3
	doc.onem_rate = 0.2

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
		_upsert_salary_component(comp_data)


def _create_drc_income_tax_slab():
	"""Create DRC IPR/PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="DRC PAYE 2025",
		currency="CDF",
		bands=[
			{"from_amount": 0, "to_amount": 162000, "rate": 3},
			{"from_amount": 162001, "to_amount": 1800000, "rate": 15},
			{"from_amount": 1800001, "to_amount": 3600000, "rate": 30},
			{"from_amount": 3600001, "to_amount": 0, "rate": 40},
		],
	)


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
	doc = frappe.get_doc("Nigeria Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.pension_employee_rate = 8
	doc.pension_employer_rate = 10
	doc.nhf_rate = 2.5
	doc.nhis_employee_rate = 5
	doc.nhis_employer_rate = 10
	doc.nsitf_rate = 1
	doc.itf_rate = 1

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
		_upsert_salary_component(comp_data)


def _create_nigeria_income_tax_slab():
	"""Create Nigeria PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Nigeria PAYE 2025",
		currency="NGN",
		bands=[
			{"from_amount": 0, "to_amount": 25000, "rate": 7},
			{"from_amount": 25001, "to_amount": 50000, "rate": 11},
			{"from_amount": 50001, "to_amount": 91667, "rate": 15},
			{"from_amount": 91668, "to_amount": 133333, "rate": 19},
			{"from_amount": 133334, "to_amount": 266667, "rate": 21},
			{"from_amount": 266668, "to_amount": 0, "rate": 24},
		],
	)


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
	doc = frappe.get_doc("Mozambique Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_employee_rate = 3
	doc.inss_employer_rate = 4

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
		_upsert_salary_component(comp_data)


def _create_mozambique_income_tax_slab():
	"""Create Mozambique PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Mozambique PAYE 2025",
		currency="MZN",
		bands=[
			{"from_amount": 0, "to_amount": 3500, "rate": 10},
			{"from_amount": 3501, "to_amount": 14000, "rate": 15},
			{"from_amount": 14001, "to_amount": 42000, "rate": 20},
			{"from_amount": 42001, "to_amount": 126000, "rate": 25},
			{"from_amount": 126001, "to_amount": 0, "rate": 32},
		],
	)


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
	doc = frappe.get_doc("Angola Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_employee_rate = 3
	doc.inss_employer_rate = 8

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
		_upsert_salary_component(comp_data)


def _create_angola_income_tax_slab():
	"""Create Angola IRT/PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Angola PAYE 2025",
		currency="AOA",
		bands=[
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
		],
	)


def setup_ethiopia():
	"""Set up Ethiopia payroll components, Income Tax Slab, and default settings."""
	_create_ethiopia_settings()
	_create_ethiopia_salary_components()
	_create_ethiopia_income_tax_slab()
	_create_salary_structure("Ethiopia Payroll Template", "ETB", [
		"PIT", "Pension Employee", "Pension Employer",
	])


def _create_ethiopia_settings():
	"""Create Ethiopia Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Ethiopia Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.pension_employee_rate = 7
	doc.pension_employer_rate = 11
	doc.pension_ceiling = 15000

	pit_bands = [
		{"from_amount": 0, "to_amount": 2000, "rate": 0},
		{"from_amount": 2001, "to_amount": 4000, "rate": 15},
		{"from_amount": 4001, "to_amount": 7000, "rate": 20},
		{"from_amount": 7001, "to_amount": 10000, "rate": 25},
		{"from_amount": 10001, "to_amount": 14000, "rate": 30},
		{"from_amount": 14001, "to_amount": 0, "rate": 35},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_ethiopia_salary_components():
	"""Create Ethiopia statutory salary components."""
	components = [
		{
			"salary_component": "PIT",
			"salary_component_abbr": "PIT",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employee",
			"salary_component_abbr": "PENSe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Pension Employer",
			"salary_component_abbr": "PENSr",
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
		_upsert_salary_component(comp_data)


def _create_ethiopia_income_tax_slab():
	"""Create Ethiopia PIT Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Ethiopia PIT 2025",
		currency="ETB",
		bands=[
			{"from_amount": 0, "to_amount": 2000, "rate": 0},
			{"from_amount": 2001, "to_amount": 4000, "rate": 15},
			{"from_amount": 4001, "to_amount": 7000, "rate": 20},
			{"from_amount": 7001, "to_amount": 10000, "rate": 25},
			{"from_amount": 10001, "to_amount": 14000, "rate": 30},
			{"from_amount": 14001, "to_amount": 0, "rate": 35},
		],
	)


def setup_south_africa():
	"""Set up South Africa payroll components, Income Tax Slab, and default settings."""
	_create_south_africa_settings()
	_create_south_africa_salary_components()
	_create_south_africa_income_tax_slab()
	_create_salary_structure("South Africa Payroll Template", "ZAR", [
		"PAYE", "UIF Employee", "UIF Employer", "SDL",
	])


def _create_south_africa_settings():
	"""Create South Africa Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("South Africa Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.threshold_under_65 = 95750
	doc.threshold_65_74 = 148217
	doc.threshold_75_plus = 165689
	doc.rebate_primary = 17235
	doc.rebate_secondary = 9444
	doc.rebate_tertiary = 3145
	doc.uif_rate = 1
	doc.uif_ceiling = 17712
	doc.sdl_applicable = 1
	doc.sdl_rate = 1

	paye_bands = [
		{"from_amount": 0, "to_amount": 237100, "rate": 18, "base_tax": 0},
		{"from_amount": 237101, "to_amount": 370500, "rate": 26, "base_tax": 42678},
		{"from_amount": 370501, "to_amount": 512800, "rate": 31, "base_tax": 77362},
		{"from_amount": 512801, "to_amount": 673000, "rate": 36, "base_tax": 121475},
		{"from_amount": 673001, "to_amount": 857900, "rate": 39, "base_tax": 179147},
		{"from_amount": 857901, "to_amount": 1817000, "rate": 41, "base_tax": 251258},
		{"from_amount": 1817001, "to_amount": 0, "rate": 45, "base_tax": 644489},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_south_africa_salary_components():
	"""Create South Africa statutory salary components."""
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
		},
		{
			"salary_component": "UIF Employee",
			"salary_component_abbr": "UIFe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "UIF Employer",
			"salary_component_abbr": "UIFr",
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
	]

	for comp_data in components:
		_upsert_salary_component(comp_data)


def _create_south_africa_income_tax_slab():
	"""Create South Africa PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="South Africa PAYE 2025",
		currency="ZAR",
		bands=[
			{"from_amount": 0, "to_amount": 237100, "rate": 18},
			{"from_amount": 237101, "to_amount": 370500, "rate": 26},
			{"from_amount": 370501, "to_amount": 512800, "rate": 31},
			{"from_amount": 512801, "to_amount": 673000, "rate": 36},
			{"from_amount": 673001, "to_amount": 857900, "rate": 39},
			{"from_amount": 857901, "to_amount": 1817000, "rate": 41},
			{"from_amount": 1817001, "to_amount": 0, "rate": 45},
		],
	)


def setup_egypt():
	"""Set up Egypt payroll components, Income Tax Slab, and default settings."""
	_create_egypt_settings()
	_create_egypt_salary_components()
	_create_egypt_income_tax_slab()
	_create_salary_structure("Egypt Payroll Template", "EGP", [
		"Income Tax", "Social Insurance Employee", "Social Insurance Employer",
		"Health Insurance Employee", "Health Insurance Employer", "Martyrs Fund",
	])


def _create_egypt_settings():
	"""Create Egypt Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Egypt Payroll Settings")
	if doc.income_tax_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.social_insurance_employee_rate = 11
	doc.social_insurance_employer_rate = 18.75
	doc.social_insurance_ceiling = 16700
	doc.health_insurance_employee_rate = 1
	doc.health_insurance_employer_rate = 3.25
	doc.personal_exemption = 15000
	doc.number_of_dependents = 0
	doc.max_dependents = 3
	doc.dependent_deduction = 3000

	income_tax_bands = [
		{"from_amount": 0, "to_amount": 40000, "rate": 0},
		{"from_amount": 40001, "to_amount": 55000, "rate": 10},
		{"from_amount": 55001, "to_amount": 70000, "rate": 15},
		{"from_amount": 70001, "to_amount": 200000, "rate": 20},
		{"from_amount": 200001, "to_amount": 400000, "rate": 22.5},
		{"from_amount": 400001, "to_amount": 1200000, "rate": 25},
		{"from_amount": 1200001, "to_amount": 0, "rate": 27.5},
	]
	for band in income_tax_bands:
		doc.append("income_tax_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_egypt_salary_components():
	"""Create Egypt statutory salary components."""
	components = [
		{
			"salary_component": "Income Tax",
			"salary_component_abbr": "IT",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Social Insurance Employee",
			"salary_component_abbr": "SICe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Social Insurance Employer",
			"salary_component_abbr": "SICr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Health Insurance Employee",
			"salary_component_abbr": "HIe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Health Insurance Employer",
			"salary_component_abbr": "HIr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Martyrs Fund",
			"salary_component_abbr": "MF",
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
		_upsert_salary_component(comp_data)


def _create_egypt_income_tax_slab():
	"""Create Egypt Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Egypt Income Tax 2025",
		currency="EGP",
		bands=[
			{"from_amount": 0, "to_amount": 40000, "rate": 0},
			{"from_amount": 40001, "to_amount": 55000, "rate": 10},
			{"from_amount": 55001, "to_amount": 70000, "rate": 15},
			{"from_amount": 70001, "to_amount": 200000, "rate": 20},
			{"from_amount": 200001, "to_amount": 400000, "rate": 22.5},
			{"from_amount": 400001, "to_amount": 1200000, "rate": 25},
			{"from_amount": 1200001, "to_amount": 0, "rate": 27.5},
		],
	)


def setup_ghana():
	"""Set up Ghana payroll components, Income Tax Slab, and default settings."""
	_create_ghana_settings()
	_create_ghana_salary_components()
	_create_ghana_income_tax_slab()
	_create_salary_structure("Ghana Payroll Template", "GHS", [
		"PAYE", "SSNIT Employee", "SSNIT Employer", "Tier 2 Pension Employer",
	])


def _create_ghana_settings():
	"""Create Ghana Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Ghana Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.ssnit_employee_rate = 5.5
	doc.ssnit_employer_rate = 13
	doc.ssnit_ceiling = 0
	doc.tier2_employer_rate = 5

	paye_bands = [
		{"from_amount": 0, "to_amount": 5880, "rate": 0},
		{"from_amount": 5881, "to_amount": 7200, "rate": 5},
		{"from_amount": 7201, "to_amount": 8760, "rate": 10},
		{"from_amount": 8761, "to_amount": 46760, "rate": 17.5},
		{"from_amount": 46761, "to_amount": 238760, "rate": 25},
		{"from_amount": 238761, "to_amount": 604760, "rate": 30},
		{"from_amount": 604761, "to_amount": 0, "rate": 35},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_ghana_salary_components():
	"""Create Ghana statutory salary components."""
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
		},
		{
			"salary_component": "SSNIT Employee",
			"salary_component_abbr": "SSNITe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "SSNIT Employer",
			"salary_component_abbr": "SSNITr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Tier 2 Pension Employer",
			"salary_component_abbr": "T2PENSr",
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
		_upsert_salary_component(comp_data)


def _create_ghana_income_tax_slab():
	"""Create Ghana PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Ghana PAYE 2025",
		currency="GHS",
		bands=[
			{"from_amount": 0, "to_amount": 5880, "rate": 0},
			{"from_amount": 5881, "to_amount": 7200, "rate": 5},
			{"from_amount": 7201, "to_amount": 8760, "rate": 10},
			{"from_amount": 8761, "to_amount": 46760, "rate": 17.5},
			{"from_amount": 46761, "to_amount": 238760, "rate": 25},
			{"from_amount": 238761, "to_amount": 604760, "rate": 30},
			{"from_amount": 604761, "to_amount": 0, "rate": 35},
		],
	)


def setup_botswana():
	"""Set up Botswana payroll components, Income Tax Slab, and default settings."""
	_create_botswana_settings()
	_create_botswana_salary_components()
	_create_botswana_income_tax_slab()
	_create_salary_structure("Botswana Payroll Template", "BWP", [
		"PAYE",
	])


def _create_botswana_settings():
	"""Create Botswana Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Botswana Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.tax_free_threshold = 48000

	paye_bands = [
		{"from_amount": 0, "to_amount": 48000, "rate": 0},
		{"from_amount": 48001, "to_amount": 96000, "rate": 5},
		{"from_amount": 96001, "to_amount": 144000, "rate": 12.5},
		{"from_amount": 144001, "to_amount": 192000, "rate": 18.75},
		{"from_amount": 192001, "to_amount": 240000, "rate": 25},
		{"from_amount": 240001, "to_amount": 0, "rate": 26.5},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_botswana_salary_components():
	"""Create Botswana statutory salary components."""
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
		},
	]

	for comp_data in components:
		_upsert_salary_component(comp_data)


def _create_botswana_income_tax_slab():
	"""Create Botswana PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Botswana PAYE 2025",
		currency="BWP",
		bands=[
			{"from_amount": 0, "to_amount": 48000, "rate": 0},
			{"from_amount": 48001, "to_amount": 96000, "rate": 5},
			{"from_amount": 96001, "to_amount": 144000, "rate": 12.5},
			{"from_amount": 144001, "to_amount": 192000, "rate": 18.75},
			{"from_amount": 192001, "to_amount": 240000, "rate": 25},
			{"from_amount": 240001, "to_amount": 0, "rate": 26.5},
		],
	)


def setup_morocco():
	"""Set up Morocco payroll components, Income Tax Slab, and default settings."""
	_create_morocco_settings()
	_create_morocco_salary_components()
	_create_morocco_income_tax_slab()
	_create_salary_structure("Morocco Payroll Template", "MAD", [
		"IR", "CNSS Employee", "CNSS Employer",
	])


def _create_morocco_settings():
	"""Create Morocco Payroll Settings with 2026 default rates."""
	doc = frappe.get_doc("Morocco Payroll Settings")
	if doc.ir_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnss_capped_rate = 4.48
	doc.cnss_uncapped_rate = 2.26
	doc.cnss_ceiling = 6000
	doc.cnss_employer_capped_rate = 8.6
	doc.cnss_employer_uncapped_rate = 4.11
	doc.professional_deduction_rate = 20
	doc.professional_deduction_ceiling = 2500
	doc.annual_exemption = 40000
	doc.number_of_dependents = 0
	doc.max_dependents_for_allowance = 6
	doc.dependent_allowance = 500

	ir_bands = [
		{"from_amount": 0, "to_amount": 40000, "rate": 0},
		{"from_amount": 40001, "to_amount": 60000, "rate": 10},
		{"from_amount": 60001, "to_amount": 80000, "rate": 20},
		{"from_amount": 80001, "to_amount": 100000, "rate": 30},
		{"from_amount": 100001, "to_amount": 150000, "rate": 34},
		{"from_amount": 150001, "to_amount": 0, "rate": 37},
	]
	for band in ir_bands:
		doc.append("ir_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_morocco_salary_components():
	"""Create Morocco statutory salary components."""
	components = [
		{
			"salary_component": "IR",
			"salary_component_abbr": "IR",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNSS Employee",
			"salary_component_abbr": "CNSSe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNSS Employer",
			"salary_component_abbr": "CNSSr",
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
		_upsert_salary_component(comp_data)


def _create_morocco_income_tax_slab():
	"""Create Morocco IR Income Tax Slab for 2026."""
	_create_income_tax_slab(
		slab_name="Morocco IR 2026",
		currency="MAD",
		bands=[
			{"from_amount": 0, "to_amount": 40000, "rate": 0},
			{"from_amount": 40001, "to_amount": 60000, "rate": 10},
			{"from_amount": 60001, "to_amount": 80000, "rate": 20},
			{"from_amount": 80001, "to_amount": 100000, "rate": 30},
			{"from_amount": 100001, "to_amount": 150000, "rate": 34},
			{"from_amount": 150001, "to_amount": 0, "rate": 37},
		],
	)


def setup_tunisia():
	"""Set up Tunisia payroll components, Income Tax Slab, and default settings."""
	_create_tunisia_settings()
	_create_tunisia_salary_components()
	_create_tunisia_income_tax_slab()
	_create_salary_structure("Tunisia Payroll Template", "TND", [
		"IRPP", "CNSS Employee", "CNSS Employer", "Social Solidarity Contribution",
	])


def _create_tunisia_settings():
	"""Create Tunisia Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Tunisia Payroll Settings")
	if doc.irpp_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnss_employee_rate = 9.18
	doc.cnss_employer_rate = 17.07
	doc.cnss_employer_export_rate = 16.57
	doc.ssc_rate = 0.5
	doc.professional_deduction_rate = 10
	doc.professional_deduction_cap = 2000

	irpp_bands = [
		{"from_amount": 0, "to_amount": 5000, "rate": 0},
		{"from_amount": 5001, "to_amount": 10000, "rate": 15},
		{"from_amount": 10001, "to_amount": 20000, "rate": 25},
		{"from_amount": 20001, "to_amount": 30000, "rate": 30},
		{"from_amount": 30001, "to_amount": 40000, "rate": 33},
		{"from_amount": 40001, "to_amount": 50000, "rate": 36},
		{"from_amount": 50001, "to_amount": 70000, "rate": 38},
		{"from_amount": 70001, "to_amount": 0, "rate": 40},
	]
	for band in irpp_bands:
		doc.append("irpp_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_tunisia_salary_components():
	"""Create Tunisia statutory salary components."""
	components = [
		{
			"salary_component": "IRPP",
			"salary_component_abbr": "IRPP",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNSS Employee",
			"salary_component_abbr": "CNSSe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNSS Employer",
			"salary_component_abbr": "CNSSr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Social Solidarity Contribution",
			"salary_component_abbr": "SSC",
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
		_upsert_salary_component(comp_data)


def _create_tunisia_income_tax_slab():
	"""Create Tunisia IRPP Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Tunisia IRPP 2025",
		currency="TND",
		bands=[
			{"from_amount": 0, "to_amount": 5000, "rate": 0},
			{"from_amount": 5001, "to_amount": 10000, "rate": 15},
			{"from_amount": 10001, "to_amount": 20000, "rate": 25},
			{"from_amount": 20001, "to_amount": 30000, "rate": 30},
			{"from_amount": 30001, "to_amount": 40000, "rate": 33},
			{"from_amount": 40001, "to_amount": 50000, "rate": 36},
			{"from_amount": 50001, "to_amount": 70000, "rate": 38},
			{"from_amount": 70001, "to_amount": 0, "rate": 40},
		],
	)


def setup_namibia():
	"""Set up Namibia payroll components, Income Tax Slab, and default settings."""
	_create_namibia_settings()
	_create_namibia_salary_components()
	_create_namibia_income_tax_slab()
	_create_salary_structure("Namibia Payroll Template", "NAD", [
		"PAYE", "Social Security Employee", "Social Security Employer",
		"VET Levy", "Employees Compensation",
	])


def _create_namibia_settings():
	"""Create Namibia Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Namibia Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.ssc_rate = 0.9
	doc.ssc_annual_ceiling = 108000
	doc.vet_levy_applicable = 1
	doc.vet_levy_rate = 1
	doc.ecf_risk_sector = "low"

	paye_bands = [
		{"from_amount": 0, "to_amount": 100000, "rate": 0, "base_tax": 0},
		{"from_amount": 100001, "to_amount": 250000, "rate": 18, "base_tax": 0},
		{"from_amount": 250001, "to_amount": 500000, "rate": 25, "base_tax": 27000},
		{"from_amount": 500001, "to_amount": 750000, "rate": 28, "base_tax": 89500},
		{"from_amount": 750001, "to_amount": 1000000, "rate": 30, "base_tax": 159500},
		{"from_amount": 1000001, "to_amount": 1500000, "rate": 32, "base_tax": 234500},
		{"from_amount": 1500001, "to_amount": 0, "rate": 37, "base_tax": 394500},
	]
	for band in paye_bands:
		doc.append("paye_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_namibia_salary_components():
	"""Create Namibia statutory salary components."""
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
		},
		{
			"salary_component": "Social Security Employee",
			"salary_component_abbr": "SSCe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Social Security Employer",
			"salary_component_abbr": "SSCr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "VET Levy",
			"salary_component_abbr": "VET",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Employees Compensation",
			"salary_component_abbr": "ECF",
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
		_upsert_salary_component(comp_data)


def _create_namibia_income_tax_slab():
	"""Create Namibia PAYE Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Namibia PAYE 2025",
		currency="NAD",
		bands=[
			{"from_amount": 0, "to_amount": 100000, "rate": 0},
			{"from_amount": 100001, "to_amount": 250000, "rate": 18},
			{"from_amount": 250001, "to_amount": 500000, "rate": 25},
			{"from_amount": 500001, "to_amount": 750000, "rate": 28},
			{"from_amount": 750001, "to_amount": 1000000, "rate": 30},
			{"from_amount": 1000001, "to_amount": 1500000, "rate": 32},
			{"from_amount": 1500001, "to_amount": 0, "rate": 37},
		],
	)


def setup_madagascar():
	"""Set up Madagascar payroll components, Income Tax Slab, and default settings."""
	_create_madagascar_settings()
	_create_madagascar_salary_components()
	_create_madagascar_income_tax_slab()
	_create_salary_structure("Madagascar Payroll Template", "MGA", [
		"IRSA", "CNaPS Employee", "CNaPS Employer",
		"Health Insurance Employee", "Health Insurance Employer", "FMFP Training Fund",
	])


def _create_madagascar_settings():
	"""Create Madagascar Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Madagascar Payroll Settings")
	if doc.irsa_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnaps_employee_rate = 1
	doc.cnaps_employer_rate = 13
	doc.health_employee_rate = 1
	doc.health_employer_rate = 5
	doc.fmfp_rate = 1
	doc.minimum_wage = 262680
	doc.ceiling_multiplier = 8
	doc.minimum_irsa = 2000

	irsa_bands = [
		{"from_amount": 0, "to_amount": 350000, "rate": 0},
		{"from_amount": 350001, "to_amount": 400000, "rate": 5},
		{"from_amount": 400001, "to_amount": 500000, "rate": 10},
		{"from_amount": 500001, "to_amount": 600000, "rate": 15},
		{"from_amount": 600001, "to_amount": 800000, "rate": 20},
		{"from_amount": 800001, "to_amount": 1000000, "rate": 25},
		{"from_amount": 1000001, "to_amount": 0, "rate": 30},
	]
	for band in irsa_bands:
		doc.append("irsa_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_madagascar_salary_components():
	"""Create Madagascar statutory salary components."""
	components = [
		{
			"salary_component": "IRSA",
			"salary_component_abbr": "IRSA",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNaPS Employee",
			"salary_component_abbr": "CNaPSe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNaPS Employer",
			"salary_component_abbr": "CNaPSr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Health Insurance Employee",
			"salary_component_abbr": "HIe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Health Insurance Employer",
			"salary_component_abbr": "HIr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "FMFP Training Fund",
			"salary_component_abbr": "FMFP",
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
		_upsert_salary_component(comp_data)


def _create_madagascar_income_tax_slab():
	"""Create Madagascar IRSA Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Madagascar IRSA 2025",
		currency="MGA",
		bands=[
			{"from_amount": 0, "to_amount": 350000, "rate": 0},
			{"from_amount": 350001, "to_amount": 400000, "rate": 5},
			{"from_amount": 400001, "to_amount": 500000, "rate": 10},
			{"from_amount": 500001, "to_amount": 600000, "rate": 15},
			{"from_amount": 600001, "to_amount": 800000, "rate": 20},
			{"from_amount": 800001, "to_amount": 1000000, "rate": 25},
			{"from_amount": 1000001, "to_amount": 0, "rate": 30},
		],
	)


def setup_ivory_coast():
	"""Set up Ivory Coast payroll components, Income Tax Slab, and default settings."""
	_create_ivory_coast_settings()
	_create_ivory_coast_salary_components()
	_create_ivory_coast_income_tax_slab()
	_create_salary_structure("Ivory Coast Payroll Template", "XOF", [
		"ITS", "CNPS Retirement Employee", "CNPS Retirement Employer",
		"CNPS Family Allowances", "Work Injury Insurance", "Vocational Training Tax",
		"Housing Construction Fund",
	])


def _create_ivory_coast_settings():
	"""Create Ivory Coast Payroll Settings with 2025 default rates."""
	doc = frappe.get_doc("Ivory Coast Payroll Settings")
	if doc.its_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnps_employee_rate = 6.3
	doc.cnps_employer_rate = 7.7
	doc.cnps_ceiling = 3375000
	doc.family_allowances_rate = 5.75
	doc.training_tax_rate = 1.2
	doc.housing_fund_rate = 1.5
	doc.work_injury_risk_class = 1
	doc.standard_deduction_rate = 20
	doc.family_shares = 1
	doc.max_shares = 5
	doc.tax_credit_per_share = 5500

	its_bands = [
		{"from_amount": 0, "to_amount": 150000, "rate": 0},
		{"from_amount": 150001, "to_amount": 300000, "rate": 12},
		{"from_amount": 300001, "to_amount": 500000, "rate": 18},
		{"from_amount": 500001, "to_amount": 1000000, "rate": 25},
		{"from_amount": 1000001, "to_amount": 2000000, "rate": 30},
		{"from_amount": 2000001, "to_amount": 0, "rate": 32},
	]
	for band in its_bands:
		doc.append("its_bands", band)

	doc.flags.ignore_permissions = True
	doc.save()


def _create_ivory_coast_salary_components():
	"""Create Ivory Coast statutory salary components."""
	components = [
		{
			"salary_component": "ITS",
			"salary_component_abbr": "ITS",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 1,
			"exempted_from_income_tax": 0,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNPS Retirement Employee",
			"salary_component_abbr": "CNPSe",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 1,
			"statistical_component": 0,
			"do_not_include_in_total": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNPS Retirement Employer",
			"salary_component_abbr": "CNPSr",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNPS Family Allowances",
			"salary_component_abbr": "FA",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Work Injury Insurance",
			"salary_component_abbr": "WII",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Vocational Training Tax",
			"salary_component_abbr": "VTT",
			"type": "Deduction",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"statistical_component": 1,
			"do_not_include_in_total": 1,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Housing Construction Fund",
			"salary_component_abbr": "HCF",
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
		_upsert_salary_component(comp_data)


def _create_ivory_coast_income_tax_slab():
	"""Create Ivory Coast ITS Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Ivory Coast ITS 2025",
		currency="XOF",
		bands=[
			{"from_amount": 0, "to_amount": 150000, "rate": 0},
			{"from_amount": 150001, "to_amount": 300000, "rate": 12},
			{"from_amount": 300001, "to_amount": 500000, "rate": 18},
			{"from_amount": 500001, "to_amount": 1000000, "rate": 25},
			{"from_amount": 1000001, "to_amount": 2000000, "rate": 30},
			{"from_amount": 2000001, "to_amount": 0, "rate": 32},
		],
	)


def setup_workspace_sidebar():
	"""Rebuild Payroll Africa workspace sidebar based on enabled countries.

	Reads the workspace_sidebar/payroll_africa.json template, filters out
	sections for disabled countries, and writes the result to the database.
	"""
	import json
	import os

	from payroll_africa.boot import COUNTRY_FIELD_MAP, get_enabled_countries

	if frappe.db.exists("Workspace Sidebar", "Payroll"):
		sidebar = frappe.get_doc("Workspace Sidebar", "Payroll")
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
			frappe.db.commit()  # nosemgrep: frappe-manual-commit

	template_path = frappe.get_app_path("payroll_africa", "workspace_sidebar", "payroll_africa.json")
	if not os.path.exists(template_path):
		return
	with open(template_path, "r") as f:  # nosemgrep: frappe-security-file-traversal
		template = json.load(f)

	enabled = get_enabled_countries()

	_settings_to_country = {}
	for country in COUNTRY_FIELD_MAP:
		if country == "Congo, The Democratic Republic of the":
			prefix = "DRC"
		else:
			prefix = country
		_settings_to_country[f"{prefix} Payroll Settings"] = country
		_settings_to_country[f"{prefix} Reports"] = country

	filtered_items = []
	skip_section = False

	for item in template.get("items", []):
		label = item.get("label", "")

		if item.get("type") == "Section Break" and label in _settings_to_country:
			country = _settings_to_country[label]
			skip_section = country not in enabled
			if skip_section:
				continue
			else:
				filtered_items.append(item)
				continue

		if label in _settings_to_country:
			country = _settings_to_country[label]
			if country not in enabled:
				continue

		if skip_section and item.get("child"):
			continue

		if item.get("type") == "Section Break":
			skip_section = False

		filtered_items.append(item)

	final_items = []
	i = 0
	while i < len(filtered_items):
		item = filtered_items[i]
		if (
			item.get("type") == "Section Break"
			and item.get("label") in ("East Africa", "Southern Africa", "West & Central Africa")
		):
			has_children = False
			j = i + 1
			while j < len(filtered_items):
				next_item = filtered_items[j]
				if next_item.get("type") == "Section Break" and not next_item.get("child"):
					break
				if next_item.get("child"):
					has_children = True
					break
				j += 1
			if not has_children:
				i += 1
				continue
		final_items.append(item)
		i += 1

	if frappe.db.exists("Workspace Sidebar", "Payroll Africa"):
		frappe.db.delete("Workspace Sidebar Item", {"parent": "Payroll Africa"})
		sidebar_doc = frappe.get_doc("Workspace Sidebar", "Payroll Africa")
	else:
		sidebar_doc = frappe.new_doc("Workspace Sidebar")
		sidebar_doc.name = template.get("name", "Payroll Africa")
		sidebar_doc.title = template.get("title", "Payroll Africa")
		sidebar_doc.module = template.get("module", "Payroll Africa")
		sidebar_doc.app = template.get("app", "payroll_africa")
		sidebar_doc.header_icon = template.get("header_icon", "globe")
		sidebar_doc.standard = 1

	sidebar_doc.items = []
	for item_data in final_items:
		sidebar_doc.append("items", {
			"label": item_data.get("label", ""),
			"link_to": item_data.get("link_to", ""),
			"link_type": item_data.get("link_type", ""),
			"type": item_data.get("type", "Link"),
			"icon": item_data.get("icon", ""),
			"child": item_data.get("child", 0),
			"collapsible": item_data.get("collapsible", 0),
			"indent": item_data.get("indent", 0),
			"keep_closed": item_data.get("keep_closed", 0),
			"show_arrow": item_data.get("show_arrow", 0),
		})

	sidebar_doc.flags.ignore_permissions = True
	sidebar_doc.save()
	frappe.db.commit()  # nosemgrep: frappe-manual-commit


def setup_desktop_icon():
	"""Create Desktop Icon for Payroll Africa under Frappe HR app."""
	if not frappe.db.exists("Desktop Icon", {"label": "Frappe HR", "icon_type": "App"}):
		return

	if frappe.db.exists("Desktop Icon", {"label": "Payroll Africa", "icon_type": "Link"}):
		existing = frappe.get_doc("Desktop Icon", {"label": "Payroll Africa", "icon_type": "Link"})
		if existing.logo_url != "/assets/payroll_africa/icons/desktop_icons/solid/payroll_africa.svg":
			existing.logo_url = "/assets/payroll_africa/icons/desktop_icons/solid/payroll_africa.svg"
			existing.flags.ignore_permissions = True
			existing.save()
			frappe.db.commit()  # nosemgrep: frappe-manual-commit
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
	frappe.db.commit()  # nosemgrep: frappe-manual-commit


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
		"Ethiopia Payroll Template", "South Africa Payroll Template",
		"Egypt Payroll Template", "Ghana Payroll Template",
		"Botswana Payroll Template", "Morocco Payroll Template",
		"Tunisia Payroll Template", "Namibia Payroll Template",
		"Madagascar Payroll Template", "Ivory Coast Payroll Template",
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
		# Ethiopia
		"PIT", "Pension Employee", "Pension Employer",
		# South Africa
		"PAYE", "UIF Employee", "UIF Employer", "SDL",
		# Egypt
		"Income Tax", "Social Insurance Employee", "Social Insurance Employer",
		"Health Insurance Employee", "Health Insurance Employer", "Martyrs Fund",
		# Ghana
		"PAYE", "SSNIT Employee", "SSNIT Employer", "Tier 2 Pension Employer",
		# Botswana
		"PAYE",
		# Morocco
		"IR", "CNSS Employee", "CNSS Employer",
		# Tunisia
		"IRPP", "CNSS Employee", "CNSS Employer", "Social Solidarity Contribution",
		# Namibia
		"PAYE", "Social Security Employee", "Social Security Employer",
		"VET Levy", "Employees Compensation",
		# Madagascar
		"IRSA", "CNaPS Employee", "CNaPS Employer",
		"Health Insurance Employee", "Health Insurance Employer", "FMFP Training Fund",
		# Ivory Coast
		"ITS", "CNPS Retirement Employee", "CNPS Retirement Employer",
		"CNPS Family Allowances", "Work Injury Insurance", "Vocational Training Tax",
		"Housing Construction Fund",
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
		"Ethiopia PIT 2025", "South Africa PAYE 2025",
		"Egypt Income Tax 2025", "Ghana PAYE 2025",
		"Botswana PAYE 2025", "Morocco IR 2026",
		"Tunisia IRPP 2025", "Namibia PAYE 2025",
		"Madagascar IRSA 2025", "Ivory Coast ITS 2025",
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
