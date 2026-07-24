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
	"DZD": {"currency_name": "Algerian Dinar", "symbol": "DA", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Santeem", "fraction_units": 100},
	"LYD": {"currency_name": "Libyan Dinar", "symbol": "LD", "number_format": "# ###.###", "smallest_currency_fraction_value": 0.001, "fraction": "Dirham", "fraction_units": 1000},
	"SDG": {"currency_name": "Sudanese Pound", "symbol": "SDG", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Piastre", "fraction_units": 100},
	"MRU": {"currency_name": "Mauritanian Ouguiya", "symbol": "UM", "number_format": "# ###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Khoums", "fraction_units": 5},
	"DJF": {"currency_name": "Djibouti Franc", "symbol": "Fdj", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Centime", "fraction_units": 100},
	"ERN": {"currency_name": "Eritrean Nakfa", "symbol": "Nfk", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"KMF": {"currency_name": "Comoro Franc", "symbol": "CF", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Centime", "fraction_units": 100},
	"SCR": {"currency_name": "Seychellois Rupee", "symbol": "SR", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"SSP": {"currency_name": "South Sudanese Pound", "symbol": "SSP", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Piaster", "fraction_units": 100},
	"SOS": {"currency_name": "Somali Shilling", "symbol": "Sh.So.", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Cent", "fraction_units": 100},
	"SLE": {"currency_name": "Sierra Leonean Leone", "symbol": "Le", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"LRD": {"currency_name": "Liberian Dollar", "symbol": "L$", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"GMD": {"currency_name": "Gambian Dalasi", "symbol": "D", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Butut", "fraction_units": 100},
	"CVE": {"currency_name": "Cape Verdean Escudo", "symbol": "$", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Centavo", "fraction_units": 100},
	"MUR": {"currency_name": "Mauritian Rupee", "symbol": "Rs", "number_format": "#,###.##", "smallest_currency_fraction_value": 0.01, "fraction": "Cent", "fraction_units": 100},
	"GNF": {"currency_name": "Guinean Franc", "symbol": "FG", "number_format": "#,###", "smallest_currency_fraction_value": 1, "fraction": "Centime", "fraction_units": 100},
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
		"Salary Structure Assignment": [
			{
				"fieldname": "payroll_country",
				"fieldtype": "Link",
				"label": "Payroll Country",
				"options": "Country",
				"insert_after": "employee",
				"description": "Date-effective payroll country for this assignment. Overrides Employee and Company country.",
				"module": "Payroll Africa",
			},
			{
				"fieldname": "payroll_africa_section",
				"fieldtype": "Section Break",
				"label": "Payroll Africa",
				"insert_after": "payroll_cost_centers",
				"module": "Payroll Africa",
			},
			{
				"fieldname": "payroll_africa_notes",
				"fieldtype": "Small Text",
				"label": "Payroll Africa Notes",
				"insert_after": "payroll_africa_section",
				"module": "Payroll Africa",
			},
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

	# Stock HRMS Salary Component ships only Earning/Deduction; this app models
	# employer-side contributions as a distinct type. Extend the Select options.
	sc_type = frappe.get_meta("Salary Component").get_field("type")
	if sc_type and "Employer Contribution" not in (sc_type.options or ""):
		frappe.make_property_setter({
			"doctype": "Salary Component",
			"fieldname": "type",
			"property": "options",
			"value": "Earning\nDeduction\nEmployer Contribution",
			"property_type": "Text",
		}, is_system_generated=False)
		frappe.clear_cache(doctype="Salary Component")


def _upsert_salary_component(comp_data: dict):
	"""Insert a Salary Component or update its setup-driven fields if it already exists."""
	name = comp_data["salary_component"]
	if frappe.db.exists("Salary Component", name):
		updates = {}
		for tag_field in ("p9a_tax_deduction_card_type", "p10a_tax_deduction_card_type"):
			tag_key = tag_field.replace("_tax_deduction_card_type", "_tag")
			if comp_data.get(tag_key):
				updates[tag_field] = comp_data[tag_key]
		for setup_field in ("type", "statistical_component", "do_not_include_in_total"):
			if setup_field in comp_data:
				updates[setup_field] = comp_data[setup_field]
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
		setup_cameroon, setup_chad, setup_central_african_republic,
		setup_congo, setup_gabon, setup_equatorial_guinea,
		setup_sao_tome_and_principe,
		setup_algeria, setup_libya, setup_sudan, setup_mauritania,
		setup_zimbabwe,
		setup_djibouti, setup_eritrea, setup_comoros,
		setup_sierra_leone, setup_liberia,
		setup_gambia, setup_cabo_verde, setup_mauritius,
		setup_senegal, setup_mali, setup_niger,
		setup_burkina_faso, setup_benin, setup_togo,
		setup_seychelles, setup_lesotho, setup_eswatini,
		setup_guinea, setup_guinea_bissau,
		setup_somalia, setup_south_sudan,
	):
		setup_fn()
	setup_workspace_sidebar()
	setup_desktop_icon()


# Frappe Country docnames that differ from COUNTRY_FIELD_MAP keys.
_COUNTRY_ALIASES = {
	"Cape Verde": "Cabo Verde",
	"Swaziland": "Eswatini",
}


def _clear_boot_cache():
	from payroll_africa.boot import BOOT_CACHE_KEY

	frappe.cache.delete_value(BOOT_CACHE_KEY)


def _enable_field_for_country(country):
	"""Return the Payroll Africa Settings enable field for a Company country, or None."""
	from payroll_africa.boot import COUNTRY_FIELD_MAP

	if not country:
		return None
	key = country if country in COUNTRY_FIELD_MAP else _COUNTRY_ALIASES.get(country)
	return COUNTRY_FIELD_MAP.get(key) if key else None


def _apply_enable_fields(fields):
	"""Enable the given settings fields (additive). Return count newly enabled."""
	if not fields:
		return 0
	settings = frappe.get_doc("Payroll Africa Settings")
	changed = False
	if not settings.enabled:
		settings.enabled = 1
		changed = True
	newly = 0
	for field in fields:
		if not settings.get(field):
			settings.set(field, 1)
			newly += 1
			changed = True
	if changed:
		settings.save(ignore_permissions=True)
		frappe.db.commit()  # nosemgrep: frappe-manual-commit
		_clear_boot_cache()
	return newly


def auto_enable_from_companies():
	"""Enable Payroll Africa countries that match existing Company countries.

	Additive only: turns matching countries on, never disables any. Enables the
	master switch if at least one company maps to a supported country.
	"""
	fields = set()
	for country in frappe.get_all("Company", pluck="country"):
		field = _enable_field_for_country(country)
		if field:
			fields.add(field)
	return {"newly_enabled": _apply_enable_fields(fields)}


def enable_country_on_company_insert(doc, method=None):
	"""Company after_insert hook: auto-enable the new company's country (additive)."""
	if not frappe.db.exists("DocType", "Payroll Africa Settings"):
		return
	field = _enable_field_for_country(getattr(doc, "country", None))
	if field:
		_apply_enable_fields({field})


def after_install():
	"""Run after app installation."""
	_run_setup()
	auto_enable_from_companies()


def after_migrate():
	"""Run after bench migrate."""
	_run_setup()


def _create_salary_structure(name, currency, deductions):
	"""Create a template Salary Structure for a country.

	Args:
		name: Salary Structure name, e.g. "Kenya Payroll Template"
		currency: Currency code, e.g. "KES"
		deductions: List of salary component names to add as deductions or employer contributions
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

	has_empr_table = "employer_contributions" in {
		f.fieldname for f in frappe.get_meta("Salary Structure").get_table_fields()
	}
	for component in deductions:
		ctype = frappe.db.get_value("Salary Component", component, "type")
		if ctype == "Employer Contribution":
			if has_empr_table:
				doc.append("employer_contributions", {
					"salary_component": component,
					"amount": 0,
				})
			# else: employer contributions are added to slips at runtime by the engine
		else:
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
	"""Create Kenya Payroll Settings with default rates (PAYE/SHIF/AHL 2025; NSSF Year 4, effective Feb 2026)."""
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
	doc.nssf_tier1_cap = 540       # NSSF Year 4 (Feb 2026): 6% of LEL 9,000
	doc.nssf_tier1_upper_limit = 9000   # Lower Earnings Limit (Tier I ceiling)
	doc.nssf_tier2_rate = 6
	doc.nssf_tier2_cap = 5940      # 6% of (UEL 108,000 - LEL 9,000); max total NSSF = 6,480
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
			"p9a_tag": "",
			"p10a_tag": "",
		},
		{
			"salary_component": "NITA",
			"salary_component_abbr": "NITA",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "SDL",
			"salary_component_abbr": "SDL",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "WCF",
			"salary_component_abbr": "WCF",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Work Injury BI",
			"salary_component_abbr": "WINJBI",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
	doc.napsa_cap = 37236          # NAPSA monthly earnings ceiling 2026 (max employee 5% = K1,861.80)
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
	doc.onem_rate = 0.5  # Ministerial Order, Aug 2025

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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Occupational Risks CD",
			"salary_component_abbr": "INSSORCD",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INSS Family Benefits CD",
			"salary_component_abbr": "INSSFBCD",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "INPP CD",
			"salary_component_abbr": "INPPCD",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "ONEM CD",
			"salary_component_abbr": "ONEMCD",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "NSITF NG",
			"salary_component_abbr": "NSITFNG",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "ITF NG",
			"salary_component_abbr": "ITFNG",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
	doc.inss_employer_rate = 15  # Presidential Decree 48/24, Jul 2025

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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "SDL",
			"salary_component_abbr": "SDL",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
	doc.personal_exemption = 20000  # Law 7/2024
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
		slab_name="Egypt IT 2025",
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Tier 2 Pension Employer",
			"salary_component_abbr": "T2PENSr",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
		{"from_amount": 48001, "to_amount": 84000, "rate": 5},
		{"from_amount": 84001, "to_amount": 120000, "rate": 12.5},
		{"from_amount": 120001, "to_amount": 156000, "rate": 18.75},
		{"from_amount": 156001, "to_amount": 192000, "rate": 25},
		{"from_amount": 192001, "to_amount": 0, "rate": 26.5},
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
			{"from_amount": 48001, "to_amount": 84000, "rate": 5},
			{"from_amount": 84001, "to_amount": 120000, "rate": 12.5},
			{"from_amount": 120001, "to_amount": 156000, "rate": 18.75},
			{"from_amount": 156001, "to_amount": 192000, "rate": 25},
			{"from_amount": 192001, "to_amount": 0, "rate": 26.5},
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
	doc.dependent_allowance = 600  # LF 50-25 (2026)

	ir_bands = [
		{"from_amount": 0, "to_amount": 40000, "rate": 0},
		{"from_amount": 40001, "to_amount": 60000, "rate": 10},
		{"from_amount": 60001, "to_amount": 80000, "rate": 20},
		{"from_amount": 80001, "to_amount": 100000, "rate": 30},
		{"from_amount": 100001, "to_amount": 180000, "rate": 34},
		{"from_amount": 180001, "to_amount": 0, "rate": 37},
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
	]

	for comp_data in components:
		_upsert_salary_component(comp_data)


def _create_morocco_income_tax_slab():
	"""Create Morocco IR Income Tax Slab for 2025."""
	_create_income_tax_slab(
		slab_name="Morocco IR 2025",
		currency="MAD",
		bands=[
			{"from_amount": 0, "to_amount": 40000, "rate": 0},
			{"from_amount": 40001, "to_amount": 60000, "rate": 10},
			{"from_amount": 60001, "to_amount": 80000, "rate": 20},
			{"from_amount": 80001, "to_amount": 100000, "rate": 30},
			{"from_amount": 100001, "to_amount": 180000, "rate": 34},
			{"from_amount": 180001, "to_amount": 0, "rate": 37},
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
	doc.cnss_employee_rate = 9.68  # LF2025 (Law 48/2024)
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
	doc.ssc_annual_ceiling = 132000  # SSC GN 8461, effective Mar 2025 (NAD 11,000/mo)
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "VET Levy",
			"salary_component_abbr": "VET",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Employees Compensation",
			"salary_component_abbr": "ECF",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "FMFP Training Fund",
			"salary_component_abbr": "FMFP",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "CNPS Family Allowances",
			"salary_component_abbr": "FA",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Work Injury Insurance",
			"salary_component_abbr": "WII",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Vocational Training Tax",
			"salary_component_abbr": "VTT",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
			"remove_if_zero_valued": 0,
			"depends_on_payment_days": 0,
		},
		{
			"salary_component": "Housing Construction Fund",
			"salary_component_abbr": "HCF",
			"type": "Employer Contribution",
			"variable_based_on_taxable_salary": 0,
			"exempted_from_income_tax": 0,
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


def setup_cameroon():
	"""Seed Cameroon Payroll Settings (rates configurable via DocType)."""
	_create_cameroon_settings()


def _create_cameroon_settings():
	"""Create Cameroon Payroll Settings (2025 rates, PwC/countrytaxcalc)."""
	doc = frappe.get_doc("Cameroon Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnps_pension_employee_rate = 4.2
	doc.cnps_pension_employer_rate = 4.2
	doc.cnps_ceiling = 750000
	doc.family_allowances_rate = 7
	doc.work_injury_risk_class = 1
	doc.professional_abatement_rate = 30
	doc.standard_deduction = 500000
	doc.pit_exemption_monthly = 62000
	doc.cac_surcharge_rate = 10
	doc.cfc_employee_rate = 1
	doc.cfc_employer_rate = 1.5
	doc.fne_rate = 1
	doc.taxe_communale_max = 2520
	pit_bands = [
		{"from_amount": 0, "to_amount": 2000000, "rate": 10},
		{"from_amount": 2000001, "to_amount": 3000000, "rate": 15},
		{"from_amount": 3000001, "to_amount": 5000000, "rate": 25},
		{"from_amount": 5000001, "to_amount": 10000000, "rate": 35},
		{"from_amount": 10000001, "to_amount": 0, "rate": 38.5},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	crtv_bands = [
		{"to_amount": 1200000, "amount": 500},
		{"to_amount": 1500000, "amount": 1000},
		{"to_amount": 2000000, "amount": 2000},
		{"to_amount": 3000000, "amount": 3000},
		{"to_amount": 5000000, "amount": 5000},
		{"to_amount": 7000000, "amount": 7000},
		{"to_amount": 10000000, "amount": 10000},
		{"to_amount": 0, "amount": 13000},
	]
	for band in crtv_bands:
		doc.append("crtv_bands", band)
	taxe_communale_bands = [
		{"to_amount": 600000, "amount": 500},
		{"to_amount": 800000, "amount": 1000},
		{"to_amount": 1000000, "amount": 1500},
		{"to_amount": 1500000, "amount": 2000},
		{"to_amount": 0, "amount": 2520},
	]
	for band in taxe_communale_bands:
		doc.append("taxe_communale_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_chad():
	"""Seed Chad Payroll Settings (rates configurable via DocType)."""
	_create_chad_settings()


def _create_chad_settings():
	"""Create Chad Payroll Settings (PwC 2024)."""
	doc = frappe.get_doc("Chad Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnps_pension_employee_rate = 3.5
	doc.cnps_pension_employer_rate = 7
	doc.cnps_ceiling = 500000
	doc.minimum_wage = 60000
	doc.family_allowances_rate = 7.5
	doc.work_injury_risk_class = 1
	pit_bands = [
		{"from_amount": 0, "to_amount": 800000, "rate": 0},
		{"from_amount": 800001, "to_amount": 6000000, "rate": 10.5},
		{"from_amount": 6000001, "to_amount": 7500000, "rate": 15},
		{"from_amount": 7500001, "to_amount": 9000000, "rate": 20},
		{"from_amount": 9000001, "to_amount": 12000000, "rate": 25},
		{"from_amount": 12000001, "to_amount": 0, "rate": 30},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_central_african_republic():
	"""Seed CAR Payroll Settings (rates configurable via DocType)."""
	_create_central_african_republic_settings()


def _create_central_african_republic_settings():
	"""Create Central African Republic Payroll Settings (remotepeople/MFW4A 2025/26)."""
	doc = frappe.get_doc("Central African Republic Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnss_employee_rate = 3
	doc.cnss_employer_rate = 19
	doc.cnss_ceiling = 600000
	doc.minimum_wage = 50000
	pit_bands = [
		{"from_amount": 0, "to_amount": 600000, "rate": 0},
		{"from_amount": 600001, "to_amount": 1800000, "rate": 10},
		{"from_amount": 1800001, "to_amount": 3600000, "rate": 20},
		{"from_amount": 3600001, "to_amount": 0, "rate": 30},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_congo():
	"""Seed Congo Payroll Settings (rates configurable via DocType)."""
	_create_congo_settings()


def _create_congo_settings():
	"""Create Congo Payroll Settings (PwC 2025)."""
	doc = frappe.get_doc("Congo Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnss_rate = 20.285
	doc.cnss_employee_rate = 4
	doc.cnss_ceiling = 1200000
	doc.cnamgs_rate = 0.5
	pit_bands = [
		{"from_amount": 0, "to_amount": 464000, "rate": 1},
		{"from_amount": 464001, "to_amount": 1000000, "rate": 10},
		{"from_amount": 1000001, "to_amount": 3000000, "rate": 25},
		{"from_amount": 3000001, "to_amount": 0, "rate": 40},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_gabon():
	"""Seed Gabon Payroll Settings (rates configurable via DocType)."""
	_create_gabon_settings()


def _create_gabon_settings():
	"""Create Gabon Payroll Settings (2026 reform, PwC)."""
	doc = frappe.get_doc("Gabon Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 5
	doc.cnss_employer_rate = 18
	doc.cnss_ceiling = 1500000
	pit_bands = [
		{"from_amount": 0, "to_amount": 1500000, "rate": 0},
		{"from_amount": 1500001, "to_amount": 1920000, "rate": 5},
		{"from_amount": 1920001, "to_amount": 2700000, "rate": 10},
		{"from_amount": 2700001, "to_amount": 3600000, "rate": 15},
		{"from_amount": 3600001, "to_amount": 5160000, "rate": 20},
		{"from_amount": 5160001, "to_amount": 7500000, "rate": 25},
		{"from_amount": 7500001, "to_amount": 0, "rate": 35},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_equatorial_guinea():
	"""Seed Equatorial Guinea Payroll Settings (rates configurable via DocType)."""
	_create_equatorial_guinea_settings()


def _create_equatorial_guinea_settings():
	"""Create Equatorial Guinea Payroll Settings (PwC Nov 2025)."""
	doc = frappe.get_doc("Equatorial Guinea Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.cnss_employee_rate = 4.5
	doc.cnss_employer_rate = 21.5
	doc.cnss_ceiling = 0
	doc.minimum_wage = 150000
	pit_bands = [
		{"from_amount": 0, "to_amount": 1400000, "rate": 0},
		{"from_amount": 1400001, "to_amount": 5000000, "rate": 10},
		{"from_amount": 5000001, "to_amount": 10000000, "rate": 15},
		{"from_amount": 10000001, "to_amount": 15000000, "rate": 20},
		{"from_amount": 15000001, "to_amount": 0, "rate": 25},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_sao_tome_and_principe():
	"""Seed Sao Tome and Principe Payroll Settings (rates configurable via DocType)."""
	_create_sao_tome_and_principe_settings()


def _create_sao_tome_and_principe_settings():
	"""Create Sao Tome and Principe Payroll Settings (INSS reform Jan 2025)."""
	doc = frappe.get_doc("Sao Tome and Principe Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.inss_employee_rate = 5
	doc.inss_employer_rate = 7
	doc.inss_ceiling = 500000
	pit_bands = [
		{"from_amount": 0, "to_amount": 600000, "rate": 0},
		{"from_amount": 600001, "to_amount": 1200000, "rate": 10},
		{"from_amount": 1200001, "to_amount": 2400000, "rate": 15},
		{"from_amount": 2400001, "to_amount": 0, "rate": 25},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_algeria():
	"""Set up Algeria payroll components, Income Tax Slab, and default settings."""
	_create_algeria_settings()
	_create_algeria_salary_components()
	_create_algeria_income_tax_slab()
	_create_salary_structure("Algeria Payroll Template", "DZD", [
		"PIT", "CNAS Employee", "CNAS Employer",
	])


def _create_algeria_settings():
	"""Create Algeria Payroll Settings (PwC + LFC 2024)."""
	doc = frappe.get_doc("Algeria Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2024-01-01"
	doc.cnas_employee_rate = 9
	doc.cnas_employer_rate = 26
	doc.cnas_ceiling = 0
	doc.training_tax_rate = 1
	pit_bands = [
		{"from_amount": 0, "to_amount": 240000, "rate": 0},
		{"from_amount": 240001, "to_amount": 480000, "rate": 23},
		{"from_amount": 480001, "to_amount": 960000, "rate": 27},
		{"from_amount": 960001, "to_amount": 1920000, "rate": 30},
		{"from_amount": 1920001, "to_amount": 3840000, "rate": 33},
		{"from_amount": 3840001, "to_amount": 0, "rate": 35},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_algeria_salary_components():
	"""Create Algeria statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNAS Employee", "salary_component_abbr": "CNASE", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNAS Employer", "salary_component_abbr": "CNASR", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_algeria_income_tax_slab():
	"""Create Algeria IRG Income Tax Slab."""
	_create_income_tax_slab(
		slab_name="Algeria IRG 2024",
		currency="DZD",
		bands=[
			{"from_amount": 0, "to_amount": 240000, "rate": 0},
			{"from_amount": 240001, "to_amount": 480000, "rate": 23},
			{"from_amount": 480001, "to_amount": 960000, "rate": 27},
			{"from_amount": 960001, "to_amount": 1920000, "rate": 30},
			{"from_amount": 1920001, "to_amount": 3840000, "rate": 33},
			{"from_amount": 3840001, "to_amount": 0, "rate": 35},
		],
	)


def setup_libya():
	"""Set up Libya payroll components, Income Tax Slab, and default settings."""
	_create_libya_settings()
	_create_libya_salary_components()
	_create_libya_income_tax_slab()
	_create_salary_structure("Libya Payroll Template", "LYD", [
		"PIT", "SSF Employee", "SSF Employer", "Solidarity Fund", "Jehad Tax",
	])


def _create_libya_settings():
	"""Create Libya Payroll Settings (SSF rates 2022, PwC 2026)."""
	doc = frappe.get_doc("Libya Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2022-09-01"
	doc.ssf_employee_rate = 5.125
	doc.ssf_employer_rate = 14.35
	doc.ssf_ceiling = 0
	doc.solidarity_fund_rate = 1
	doc.tax_free_threshold = 0
	pit_bands = [
		{"from_amount": 0, "to_amount": 12000, "rate": 5},
		{"from_amount": 12001, "to_amount": 0, "rate": 10},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_libya_salary_components():
	"""Create Libya statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "SSF Employee", "salary_component_abbr": "SSFe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "SSF Employer", "salary_component_abbr": "SSFr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "Solidarity Fund", "salary_component_abbr": "SOL", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "Jehad Tax", "salary_component_abbr": "JHD", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_libya_income_tax_slab():
	"""Create Libya PIT Income Tax Slab."""
	_create_income_tax_slab(
		slab_name="Libya PIT 2025",
		currency="LYD",
		bands=[
			{"from_amount": 0, "to_amount": 12000, "rate": 5},
			{"from_amount": 12001, "to_amount": 0, "rate": 10},
		],
	)


def setup_sudan():
	"""Set up Sudan payroll components, Income Tax Slab, and default settings (estimates — CONFIRM-NEEDED)."""
	_create_sudan_settings()
	_create_sudan_salary_components()
	_create_sudan_income_tax_slab()
	_create_salary_structure("Sudan Payroll Template", "SDG", [
		"PIT", "NSIF Employee", "NSIF Employer",
	])


def _create_sudan_settings():
	"""Create Sudan Payroll Settings (estimates — CONFIRM-NEEDED, conflict-affected)."""
	doc = frappe.get_doc("Sudan Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.nsif_employee_rate = 8
	doc.nsif_employer_rate = 17
	doc.nsif_ceiling = 100000
	doc.tax_free_threshold = 0
	pit_bands = [
		{"from_amount": 0, "to_amount": 120000, "rate": 0},
		{"from_amount": 120001, "to_amount": 360000, "rate": 10},
		{"from_amount": 360001, "to_amount": 720000, "rate": 15},
		{"from_amount": 720001, "to_amount": 0, "rate": 20},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_sudan_salary_components():
	"""Create Sudan statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "NSIF Employee", "salary_component_abbr": "NSIFe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "NSIF Employer", "salary_component_abbr": "NSIFr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_sudan_income_tax_slab():
	"""Create Sudan PIT Income Tax Slab (estimates — CONFIRM-NEEDED)."""
	_create_income_tax_slab(
		slab_name="Sudan PIT 2025",
		currency="SDG",
		bands=[
			{"from_amount": 0, "to_amount": 120000, "rate": 0},
			{"from_amount": 120001, "to_amount": 360000, "rate": 10},
			{"from_amount": 360001, "to_amount": 720000, "rate": 15},
			{"from_amount": 720001, "to_amount": 0, "rate": 20},
		],
	)


def setup_mauritania():
	"""Set up Mauritania payroll components, Income Tax Slab, and default settings."""
	_create_mauritania_settings()
	_create_mauritania_salary_components()
	_create_mauritania_income_tax_slab()
	_create_salary_structure("Mauritania Payroll Template", "MRU", [
		"PIT", "CNSS Employee", "CNSS Employer", "CNAM Health Employee", "CNAM Health Employer",
	])


def _create_mauritania_settings():
	"""Create Mauritania Payroll Settings (PwC 2026)."""
	doc = frappe.get_doc("Mauritania Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 1
	doc.cnss_employer_rate = 15
	doc.cnss_ceiling = 15000
	doc.cnam_employee_rate = 4
	doc.cnam_employer_rate = 5
	doc.tax_free_threshold = 72000
	pit_bands = [
		{"from_amount": 0, "to_amount": 72000, "rate": 0},
		{"from_amount": 72001, "to_amount": 108000, "rate": 15},
		{"from_amount": 108001, "to_amount": 252000, "rate": 25},
		{"from_amount": 252001, "to_amount": 0, "rate": 40},
	]
	for band in pit_bands:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_mauritania_salary_components():
	"""Create Mauritania statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNSS Employee", "salary_component_abbr": "CNSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNSS Employer", "salary_component_abbr": "CNSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "CNAM Health Employee", "salary_component_abbr": "CNAMe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNAM Health Employer", "salary_component_abbr": "CNAMr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_mauritania_income_tax_slab():
	"""Create Mauritania ITS Income Tax Slab."""
	_create_income_tax_slab(
		slab_name="Mauritania ITS 2026",
		currency="MRU",
		bands=[
			{"from_amount": 0, "to_amount": 72000, "rate": 0},
			{"from_amount": 72001, "to_amount": 108000, "rate": 15},
			{"from_amount": 108001, "to_amount": 252000, "rate": 25},
			{"from_amount": 252001, "to_amount": 0, "rate": 40},
		],
	)


def setup_zimbabwe():
	"""Seed Zimbabwe Payroll Settings (PAYE hardcoded; band table has no deduction field)."""
	_create_zimbabwe_settings()


def _create_zimbabwe_settings():
	"""Create Zimbabwe Payroll Settings (NSSA USD 700/mo ceiling, 2025)."""
	doc = frappe.get_doc("Zimbabwe Payroll Settings")
	if doc.nssa_rate:
		return
	doc.enabled = 1
	doc.effective_from = "2025-01-01"
	doc.currency_mode = "USD"
	doc.tax_free_threshold = 100
	doc.nssa_rate = 4.5
	doc.nssa_annual_ceiling = 8400
	doc.aids_levy_rate = 3
	doc.flags.ignore_permissions = True
	doc.save()


def setup_djibouti():
	"""Set up Djibouti payroll components, Income Tax Slab, and default settings."""
	_create_djibouti_settings()
	_create_djibouti_salary_components()
	_create_djibouti_income_tax_slab()
	_create_salary_structure("Djibouti Payroll Template", "DJF", ["PIT", "CNSS Employee", "CNSS Employer"])


def _create_djibouti_settings():
	"""Create Djibouti Payroll Settings (PwC WWTS 2024; ISSA health branch 2%/5%)."""
	doc = frappe.get_doc("Djibouti Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 2
	doc.cnss_employer_rate = 5
	doc.cnss_ceiling = 400000
	doc.minimum_wage = 40000
	doc.pit_threshold = 240000
	for band in [
		{"from_amount": 0, "to_amount": 240000, "rate": 0},
		{"from_amount": 240001, "to_amount": 600000, "rate": 10},
		{"from_amount": 600001, "to_amount": 1200000, "rate": 20},
		{"from_amount": 1200001, "to_amount": 0, "rate": 30},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_djibouti_salary_components():
	"""Create Djibouti statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNSS Employee", "salary_component_abbr": "CNSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNSS Employer", "salary_component_abbr": "CNSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_djibouti_income_tax_slab():
	"""Create Djibouti PIT Income Tax Slab (PwC 2024)."""
	_create_income_tax_slab(slab_name="Djibouti PIT 2026", currency="DJF", bands=[
		{"from_amount": 0, "to_amount": 240000, "rate": 0},
		{"from_amount": 240001, "to_amount": 600000, "rate": 10},
		{"from_amount": 600001, "to_amount": 1200000, "rate": 20},
		{"from_amount": 1200001, "to_amount": 0, "rate": 30},
	])


def setup_eritrea():
	"""Set up Eritrea payroll components, Income Tax Slab, and default settings."""
	_create_eritrea_settings()
	_create_eritrea_salary_components()
	_create_eritrea_income_tax_slab()
	_create_salary_structure("Eritrea Payroll Template", "ERN", ["PIT", "NICE Employee", "NICE Employer"])


def _create_eritrea_settings():
	"""Create Eritrea Payroll Settings (NICE 6%/6% ISSA; PAYE monthly bands 2024-25)."""
	doc = frappe.get_doc("Eritrea Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.nice_employee_rate = 6
	doc.nice_employer_rate = 6
	doc.nice_ceiling = 0
	doc.tax_free_threshold = 800
	for band in [
		{"from_amount": 0, "to_amount": 800, "rate": 0},
		{"from_amount": 801, "to_amount": 1000, "rate": 5},
		{"from_amount": 1001, "to_amount": 1500, "rate": 10},
		{"from_amount": 1501, "to_amount": 2000, "rate": 15},
		{"from_amount": 2001, "to_amount": 3000, "rate": 20},
		{"from_amount": 3001, "to_amount": 0, "rate": 30},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_eritrea_salary_components():
	"""Create Eritrea statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "NICE Employee", "salary_component_abbr": "NICEe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "NICE Employer", "salary_component_abbr": "NICEr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_eritrea_income_tax_slab():
	"""Create Eritrea PAYE Income Tax Slab (monthly bands)."""
	_create_income_tax_slab(slab_name="Eritrea PAYE 2026", currency="ERN", bands=[
		{"from_amount": 0, "to_amount": 800, "rate": 0},
		{"from_amount": 801, "to_amount": 1000, "rate": 5},
		{"from_amount": 1001, "to_amount": 1500, "rate": 10},
		{"from_amount": 1501, "to_amount": 2000, "rate": 15},
		{"from_amount": 2001, "to_amount": 3000, "rate": 20},
		{"from_amount": 3001, "to_amount": 0, "rate": 30},
	])


def setup_comoros():
	"""Set up Comoros payroll components, Income Tax Slab, and default settings (CNSS split CONFIRM-NEEDED)."""
	_create_comoros_settings()
	_create_comoros_salary_components()
	_create_comoros_income_tax_slab()
	_create_salary_structure("Comoros Payroll Template", "KMF", ["PIT", "CNSS Employee", "CNSS Employer"])


def _create_comoros_settings():
	"""Create Comoros Payroll Settings (CNSS split + PIT bands CONFIRM-NEEDED, estimates)."""
	doc = frappe.get_doc("Comoros Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 3.5
	doc.cnss_employer_rate = 10.5
	doc.cnss_ceiling = 0
	doc.minimum_wage = 55000
	doc.pit_threshold = 360000
	for band in [
		{"from_amount": 0, "to_amount": 360000, "rate": 0},
		{"from_amount": 360001, "to_amount": 720000, "rate": 10},
		{"from_amount": 720001, "to_amount": 1440000, "rate": 15},
		{"from_amount": 1440001, "to_amount": 2880000, "rate": 20},
		{"from_amount": 2880001, "to_amount": 0, "rate": 30},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_comoros_salary_components():
	"""Create Comoros statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNSS Employee", "salary_component_abbr": "CNSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNSS Employer", "salary_component_abbr": "CNSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_comoros_income_tax_slab():
	"""Create Comoros PIT Income Tax Slab (estimated bands — CONFIRM-NEEDED)."""
	_create_income_tax_slab(slab_name="Comoros PIT 2026", currency="KMF", bands=[
		{"from_amount": 0, "to_amount": 360000, "rate": 0},
		{"from_amount": 360001, "to_amount": 720000, "rate": 10},
		{"from_amount": 720001, "to_amount": 1440000, "rate": 15},
		{"from_amount": 1440001, "to_amount": 2880000, "rate": 20},
		{"from_amount": 2880001, "to_amount": 0, "rate": 30},
	])


def setup_sierra_leone():
	"""Set up Sierra Leone payroll components, Income Tax Slab, and default settings."""
	_create_sierra_leone_settings()
	_create_sierra_leone_salary_components()
	_create_sierra_leone_income_tax_slab()
	_create_salary_structure("Sierra Leone Payroll Template", "SLE", ["PAYE", "NASSIT Employee", "NASSIT Employer"])


def _create_sierra_leone_settings():
	"""Create Sierra Leone Payroll Settings (2026; Income Tax Act 2000 structure, SLE scale)."""
	doc = frappe.get_doc("Sierra Leone Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.tax_free_threshold = 6000
	doc.nassit_employee_rate = 5
	doc.nassit_employer_rate = 10
	doc.nassit_ceiling = 0
	for band in [
		{"from_amount": 0, "to_amount": 6000, "rate": 0},
		{"from_amount": 6001, "to_amount": 12000, "rate": 15},
		{"from_amount": 12001, "to_amount": 18000, "rate": 20},
		{"from_amount": 18001, "to_amount": 24000, "rate": 25},
		{"from_amount": 24001, "to_amount": 0, "rate": 30},
	]:
		doc.append("paye_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_sierra_leone_salary_components():
	"""Create Sierra Leone statutory salary components."""
	for comp_data in [
		{"salary_component": "PAYE", "salary_component_abbr": "PAYE", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "NASSIT Employee", "salary_component_abbr": "NASSITe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "NASSIT Employer", "salary_component_abbr": "NASSITr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_sierra_leone_income_tax_slab():
	"""Create Sierra Leone PAYE Income Tax Slab (2026, SLE)."""
	_create_income_tax_slab(slab_name="Sierra Leone PAYE 2026", currency="SLE", bands=[
		{"from_amount": 0, "to_amount": 6000, "rate": 0},
		{"from_amount": 6001, "to_amount": 12000, "rate": 15},
		{"from_amount": 12001, "to_amount": 18000, "rate": 20},
		{"from_amount": 18001, "to_amount": 24000, "rate": 25},
		{"from_amount": 24001, "to_amount": 0, "rate": 30},
	])


def setup_liberia():
	"""Set up Liberia payroll components, Income Tax Slab, and default settings."""
	_create_liberia_settings()
	_create_liberia_salary_components()
	_create_liberia_income_tax_slab()
	_create_salary_structure("Liberia Payroll Template", "LRD", ["PAYE", "NASSCorp Employee", "NASSCorp Employer"])


def _create_liberia_settings():
	"""Create Liberia Payroll Settings (PwC 14 Jan 2026)."""
	doc = frappe.get_doc("Liberia Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.tax_free_threshold = 70000
	doc.nasscorp_employee_rate = 4
	doc.nasscorp_employer_rate = 6
	doc.nasscorp_ceiling = 0
	for band in [
		{"from_amount": 0, "to_amount": 70000, "rate": 0},
		{"from_amount": 70001, "to_amount": 200000, "rate": 5},
		{"from_amount": 200001, "to_amount": 800000, "rate": 15},
		{"from_amount": 800001, "to_amount": 0, "rate": 25},
	]:
		doc.append("paye_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_liberia_salary_components():
	"""Create Liberia statutory salary components."""
	for comp_data in [
		{"salary_component": "PAYE", "salary_component_abbr": "PAYE", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "NASSCorp Employee", "salary_component_abbr": "NASSCPe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "NASSCorp Employer", "salary_component_abbr": "NASCPr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_liberia_income_tax_slab():
	"""Create Liberia PAYE Income Tax Slab (PwC 2026)."""
	_create_income_tax_slab(slab_name="Liberia PAYE 2026", currency="LRD", bands=[
		{"from_amount": 0, "to_amount": 70000, "rate": 0},
		{"from_amount": 70001, "to_amount": 200000, "rate": 5},
		{"from_amount": 200001, "to_amount": 800000, "rate": 15},
		{"from_amount": 800001, "to_amount": 0, "rate": 25},
	])


def setup_gambia():
	"""Set up Gambia payroll components, Income Tax Slab, and default settings."""
	_create_gambia_settings()
	_create_gambia_salary_components()
	_create_gambia_income_tax_slab()
	_create_salary_structure("Gambia Payroll Template", "GMD", ["PIT", "SSHFC Employee", "SSHFC Employer"])


def _create_gambia_settings():
	"""Create Gambia Payroll Settings (2026, GRA/taxrates.cc)."""
	doc = frappe.get_doc("Gambia Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.sshfc_employee_rate = 5
	doc.sshfc_employer_rate = 10
	doc.sshfc_ceiling = 25000
	doc.tax_free_threshold = 7500
	for band in [
		{"from_amount": 0, "to_amount": 7500, "rate": 0},
		{"from_amount": 7501, "to_amount": 17500, "rate": 10},
		{"from_amount": 17501, "to_amount": 27500, "rate": 15},
		{"from_amount": 27501, "to_amount": 37500, "rate": 20},
		{"from_amount": 37501, "to_amount": 47500, "rate": 25},
		{"from_amount": 47501, "to_amount": 0, "rate": 35},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_gambia_salary_components():
	"""Create Gambia statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "SSHFC Employee", "salary_component_abbr": "SSHFCe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "SSHFC Employer", "salary_component_abbr": "SSHFCr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_gambia_income_tax_slab():
	"""Create Gambia PIT Income Tax Slab (2026)."""
	_create_income_tax_slab(slab_name="Gambia PIT 2026", currency="GMD", bands=[
		{"from_amount": 0, "to_amount": 7500, "rate": 0},
		{"from_amount": 7501, "to_amount": 17500, "rate": 10},
		{"from_amount": 17501, "to_amount": 27500, "rate": 15},
		{"from_amount": 27501, "to_amount": 37500, "rate": 20},
		{"from_amount": 37501, "to_amount": 47500, "rate": 25},
		{"from_amount": 47501, "to_amount": 0, "rate": 35},
	])


def setup_cabo_verde():
	"""Set up Cabo Verde payroll components, Income Tax Slab, and default settings."""
	_create_cabo_verde_settings()
	_create_cabo_verde_salary_components()
	_create_cabo_verde_income_tax_slab()
	_create_salary_structure("Cabo Verde Payroll Template", "CVE", ["PIT", "INPS Employee", "INPS Employer", "Work Injury Insurance"])


def _create_cabo_verde_settings():
	"""Create Cabo Verde Payroll Settings (PwC 2026)."""
	doc = frappe.get_doc("Cabo Verde Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.inps_employee_rate = 8.5
	doc.inps_employer_rate = 16
	doc.inps_ceiling = 80000
	doc.work_injury_rate = 2
	doc.tax_free_threshold = 220000
	for band in [
		{"from_amount": 0, "to_amount": 220000, "rate": 0},
		{"from_amount": 220001, "to_amount": 960000, "rate": 16.5},
		{"from_amount": 960001, "to_amount": 1800000, "rate": 23.1},
		{"from_amount": 1800001, "to_amount": 0, "rate": 27.5},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_cabo_verde_salary_components():
	"""Create Cabo Verde statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "PIT", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "INPS Employee", "salary_component_abbr": "INPSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "INPS Employer", "salary_component_abbr": "INPSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "Work Injury Insurance", "salary_component_abbr": "WII", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0, "statistical_component": 1, "do_not_include_in_total": 1},
	]:
		_upsert_salary_component(comp_data)


def _create_cabo_verde_income_tax_slab():
	"""Create Cabo Verde IRPC Income Tax Slab (PwC 2026)."""
	_create_income_tax_slab(slab_name="Cabo Verde IRPC 2026", currency="CVE", bands=[
		{"from_amount": 0, "to_amount": 220000, "rate": 0},
		{"from_amount": 220001, "to_amount": 960000, "rate": 16.5},
		{"from_amount": 960001, "to_amount": 1800000, "rate": 23.1},
		{"from_amount": 1800001, "to_amount": 0, "rate": 27.5},
	])


def setup_mauritius():
	"""Set up Mauritius payroll components, Income Tax Slab, and default settings."""
	_create_mauritius_settings()
	_create_mauritius_salary_components()
	_create_mauritius_income_tax_slab()
	_create_salary_structure("Mauritius Payroll Template", "MUR", ["PAYE", "NSF Employee", "NSF Employer", "CSG", "CSG Employer", "HRDC Levy", "PRGF"])


def _create_mauritius_settings():
	"""Create Mauritius Payroll Settings (PwC/MRA 2026)."""
	doc = frappe.get_doc("Mauritius Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.nsf_employee_rate = 1
	doc.nsf_employer_rate = 2.5
	doc.nsf_ceiling = 28570
	doc.csg_rate = 1.5
	doc.csg_employer_rate = 3
	doc.csg_high_threshold = 50000
	doc.csg_employee_high_rate = 3
	doc.csg_employer_high_rate = 6
	doc.hrdc_rate = 1.5
	doc.prgf_applicable = 1
	doc.prgf_rate = 4.5
	doc.prgf_exemption_threshold = 200000
	doc.fair_share_applicable = 1
	doc.fair_share_threshold = 12000000
	doc.fair_share_rate = 15
	doc.exempt_threshold_monthly = 38462
	for band in [
		{"from_amount": 0, "to_amount": 500000, "rate": 0},
		{"from_amount": 500001, "to_amount": 1000000, "rate": 10},
		{"from_amount": 1000001, "to_amount": 0, "rate": 20},
	]:
		doc.append("paye_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_mauritius_salary_components():
	"""Create Mauritius statutory salary components."""
	for comp_data in [
		{"salary_component": "PAYE", "salary_component_abbr": "PAYE", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "NSF Employee", "salary_component_abbr": "NSFe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "NSF Employer", "salary_component_abbr": "NSFr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "CSG", "salary_component_abbr": "CSG", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CSG Employer", "salary_component_abbr": "CSGr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "HRDC Levy", "salary_component_abbr": "HRDC", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "PRGF", "salary_component_abbr": "PRGF", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "Fair Share Contribution", "salary_component_abbr": "FSC", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0, "remove_if_zero_valued": 1},
	]:
		_upsert_salary_component(comp_data)


def _create_mauritius_income_tax_slab():
	"""Create Mauritius PAYE Income Tax Slab (2026)."""
	_create_income_tax_slab(slab_name="Mauritius PAYE 2026", currency="MUR", bands=[
		{"from_amount": 0, "to_amount": 500000, "rate": 0},
		{"from_amount": 500001, "to_amount": 1000000, "rate": 10},
		{"from_amount": 1000001, "to_amount": 0, "rate": 20},
	])


def setup_senegal():
	"""Set up Senegal payroll components, Income Tax Slab, and default settings (PwC 2026)."""
	_create_senegal_settings()
	_create_senegal_salary_components()
	_create_senegal_income_tax_slab()
	_create_salary_structure("Senegal Payroll Template", "XOF", ["Income Tax", "IPRES Pension Employee", "IPRES Pension Employer", "CSS Health Employer", "AMO Health Employee", "AMO Health Employer"])


def _create_senegal_settings():
	"""Create Senegal Payroll Settings (PwC 2026)."""
	doc = frappe.get_doc("Senegal Payroll Settings")
	if doc.income_tax_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.ipres_employee_rate = 5.6
	doc.ipres_employer_rate = 8.4
	doc.ipres_ceiling = 432000
	doc.minimum_wage = 74750
	doc.ipres_ceiling_multiplier = 6
	doc.css_employee_rate = 0
	doc.css_employer_rate = 7
	doc.css_ceiling = 432000
	doc.amo_applicable = 0
	doc.amo_employee_rate = 3
	doc.amo_employer_rate = 3
	doc.amo_ceiling = 250000
	doc.tax_free_threshold_annual = 630000
	doc.number_of_dependent_children = 0
	doc.child_deduction = 100000
	doc.max_deductible_children = 6
	for band in [
		{"from_amount": 0, "to_amount": 630000, "rate": 0},
		{"from_amount": 630001, "to_amount": 1500000, "rate": 20},
		{"from_amount": 1500001, "to_amount": 4000000, "rate": 30},
		{"from_amount": 4000001, "to_amount": 8000000, "rate": 35},
		{"from_amount": 8000001, "to_amount": 13500000, "rate": 37},
		{"from_amount": 13500001, "to_amount": 50000000, "rate": 40},
		{"from_amount": 50000001, "to_amount": 0, "rate": 43},
	]:
		doc.append("income_tax_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_senegal_salary_components():
	"""Create Senegal statutory salary components."""
	for comp_data in [
		{"salary_component": "Income Tax", "salary_component_abbr": "IR", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "IPRES Pension Employee", "salary_component_abbr": "IPRESe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "IPRES Pension Employer", "salary_component_abbr": "IPRESr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "CSS Health Employer", "salary_component_abbr": "CSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "AMO Health Employee", "salary_component_abbr": "AMOe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "AMO Health Employer", "salary_component_abbr": "AMOr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_senegal_income_tax_slab():
	"""Create Senegal IR Income Tax Slab (PwC 2026)."""
	_create_income_tax_slab(slab_name="Senegal IR 2026", currency="XOF", bands=[
		{"from_amount": 0, "to_amount": 630000, "rate": 0},
		{"from_amount": 630001, "to_amount": 1500000, "rate": 20},
		{"from_amount": 1500001, "to_amount": 4000000, "rate": 30},
		{"from_amount": 4000001, "to_amount": 8000000, "rate": 35},
		{"from_amount": 8000001, "to_amount": 13500000, "rate": 37},
		{"from_amount": 13500001, "to_amount": 50000000, "rate": 40},
		{"from_amount": 50000001, "to_amount": 0, "rate": 43},
	])


def setup_mali():
	"""Set up Mali payroll components, Income Tax Slab, and default settings (INPS/DGI 2025)."""
	_create_mali_settings()
	_create_mali_salary_components()
	_create_mali_income_tax_slab()
	_create_salary_structure("Mali Payroll Template", "XOF", ["PIT", "INSS Pension Employee", "INSS Pension Employer", "AMO Health Employee", "AMO Health Employer"])


def _create_mali_settings():
	"""Create Mali Payroll Settings (INPS/DGI 2025)."""
	doc = frappe.get_doc("Mali Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.inss_employee_rate = 3.6
	doc.inss_employer_rate = 5.4
	doc.minimum_wage = 75000
	doc.amo_employee_rate = 2
	doc.amo_employer_rate = 3.5
	doc.pit_threshold = 175000
	for band in [
		{"from_amount": 0, "to_amount": 175000, "rate": 0},
		{"from_amount": 175001, "to_amount": 600000, "rate": 5},
		{"from_amount": 600001, "to_amount": 1200000, "rate": 13},
		{"from_amount": 1200001, "to_amount": 1800000, "rate": 20},
		{"from_amount": 1800001, "to_amount": 2400000, "rate": 28},
		{"from_amount": 2400001, "to_amount": 3500000, "rate": 34},
		{"from_amount": 3500001, "to_amount": 0, "rate": 40},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_mali_salary_components():
	"""Create Mali statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "ITS", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "INSS Pension Employee", "salary_component_abbr": "INPSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "INSS Pension Employer", "salary_component_abbr": "INPSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "AMO Health Employee", "salary_component_abbr": "AMOe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "AMO Health Employer", "salary_component_abbr": "AMOr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_mali_income_tax_slab():
	"""Create Mali ITS Income Tax Slab (DGI, monthly bands)."""
	_create_income_tax_slab(slab_name="Mali ITS 2025", currency="XOF", bands=[
		{"from_amount": 0, "to_amount": 175000, "rate": 0},
		{"from_amount": 175001, "to_amount": 600000, "rate": 5},
		{"from_amount": 600001, "to_amount": 1200000, "rate": 13},
		{"from_amount": 1200001, "to_amount": 1800000, "rate": 20},
		{"from_amount": 1800001, "to_amount": 2400000, "rate": 28},
		{"from_amount": 2400001, "to_amount": 3500000, "rate": 34},
		{"from_amount": 3500001, "to_amount": 0, "rate": 40},
	])


def setup_niger():
	"""Set up Niger payroll components, Income Tax Slab, and default settings (CNSS/DGI 2025)."""
	_create_niger_settings()
	_create_niger_salary_components()
	_create_niger_income_tax_slab()
	_create_salary_structure("Niger Payroll Template", "XOF", ["PIT", "CNSS Pension Employee", "CNSS Pension Employer", "AMO Health Employee", "AMO Health Employer"])


def _create_niger_settings():
	"""Create Niger Payroll Settings (CNSS/DGI 2025)."""
	doc = frappe.get_doc("Niger Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 5.25
	doc.cnss_employer_rate = 16.4
	doc.cnss_ceiling = 500000
	doc.minimum_wage = 40000
	doc.amo_employee_rate = 2.5
	doc.amo_employer_rate = 4.5
	doc.pit_threshold = 25000
	for band in [
		{"from_amount": 0, "to_amount": 25000, "rate": 0},
		{"from_amount": 25001, "to_amount": 50000, "rate": 2},
		{"from_amount": 50001, "to_amount": 100000, "rate": 6},
		{"from_amount": 100001, "to_amount": 150000, "rate": 13},
		{"from_amount": 150001, "to_amount": 300000, "rate": 25},
		{"from_amount": 300001, "to_amount": 400000, "rate": 30},
		{"from_amount": 400001, "to_amount": 700000, "rate": 32},
		{"from_amount": 700001, "to_amount": 1000000, "rate": 34},
		{"from_amount": 1000001, "to_amount": 0, "rate": 35},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_niger_salary_components():
	"""Create Niger statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "ITS", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNSS Pension Employee", "salary_component_abbr": "CNSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNSS Pension Employer", "salary_component_abbr": "CNSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "AMO Health Employee", "salary_component_abbr": "AMOe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "AMO Health Employer", "salary_component_abbr": "AMOr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_niger_income_tax_slab():
	"""Create Niger ITS Income Tax Slab (DGI, monthly bands)."""
	_create_income_tax_slab(slab_name="Niger ITS 2025", currency="XOF", bands=[
		{"from_amount": 0, "to_amount": 25000, "rate": 0},
		{"from_amount": 25001, "to_amount": 50000, "rate": 2},
		{"from_amount": 50001, "to_amount": 100000, "rate": 6},
		{"from_amount": 100001, "to_amount": 150000, "rate": 13},
		{"from_amount": 150001, "to_amount": 300000, "rate": 25},
		{"from_amount": 300001, "to_amount": 400000, "rate": 30},
		{"from_amount": 400001, "to_amount": 700000, "rate": 32},
		{"from_amount": 700001, "to_amount": 1000000, "rate": 34},
		{"from_amount": 1000001, "to_amount": 0, "rate": 35},
	])


def setup_burkina_faso():
	"""Set up Burkina Faso payroll components, Income Tax Slab, and default settings."""
	_create_burkina_faso_settings()
	_create_burkina_faso_salary_components()
	_create_burkina_faso_income_tax_slab()
	_create_salary_structure("Burkina Faso Payroll Template", "XOF", ["PIT", "CNSS Pension Employee", "CNSS Pension Employer", "AMO Health Employee", "AMO Health Employer"])


def _create_burkina_faso_settings():
	"""Create Burkina Faso Payroll Settings (CNSS/DGI 2026)."""
	doc = frappe.get_doc("Burkina Faso Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 8
	doc.cnss_employer_rate = 17.5
	doc.cnss_ceiling = 800000
	doc.minimum_wage = 45000
	doc.amo_employee_rate = 2.5
	doc.amo_employer_rate = 2.5
	doc.pit_threshold = 30000
	for band in [
		{"from_amount": 0, "to_amount": 30000, "rate": 0},
		{"from_amount": 30001, "to_amount": 50000, "rate": 12.1},
		{"from_amount": 50001, "to_amount": 80000, "rate": 13.9},
		{"from_amount": 80001, "to_amount": 120000, "rate": 15.7},
		{"from_amount": 120001, "to_amount": 170000, "rate": 18.4},
		{"from_amount": 170001, "to_amount": 250000, "rate": 21.7},
		{"from_amount": 250001, "to_amount": 0, "rate": 25},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_burkina_faso_salary_components():
	"""Create Burkina Faso statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "IUTS", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNSS Pension Employee", "salary_component_abbr": "CNSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNSS Pension Employer", "salary_component_abbr": "CNSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "AMO Health Employee", "salary_component_abbr": "AMOe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "AMO Health Employer", "salary_component_abbr": "AMOr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_burkina_faso_income_tax_slab():
	"""Create Burkina Faso IUTS Income Tax Slab (monthly bands)."""
	_create_income_tax_slab(slab_name="Burkina Faso IUTS 2026", currency="XOF", bands=[
		{"from_amount": 0, "to_amount": 30000, "rate": 0},
		{"from_amount": 30001, "to_amount": 50000, "rate": 12.1},
		{"from_amount": 50001, "to_amount": 80000, "rate": 13.9},
		{"from_amount": 80001, "to_amount": 120000, "rate": 15.7},
		{"from_amount": 120001, "to_amount": 170000, "rate": 18.4},
		{"from_amount": 170001, "to_amount": 250000, "rate": 21.7},
		{"from_amount": 250001, "to_amount": 0, "rate": 25},
	])


def setup_benin():
	"""Set up Benin payroll components, Income Tax Slab, and default settings."""
	_create_benin_settings()
	_create_benin_salary_components()
	_create_benin_income_tax_slab()
	_create_salary_structure("Benin Payroll Template", "XOF", ["PIT", "CNSS Pension Employee", "CNSS Pension Employer"])


def _create_benin_settings():
	"""Create Benin Payroll Settings (CNSS.bj + CGI 2026; ITS 6-band top 40%)."""
	doc = frappe.get_doc("Benin Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 3.6
	doc.cnss_employer_rate = 15.4
	doc.cnss_ceiling = 0
	doc.minimum_wage = 52000
	doc.amo_employee_rate = 0
	doc.amo_employer_rate = 0
	doc.pit_threshold = 60000
	for band in [
		{"from_amount": 0, "to_amount": 60000, "rate": 0},
		{"from_amount": 60001, "to_amount": 150000, "rate": 10},
		{"from_amount": 150001, "to_amount": 250000, "rate": 15},
		{"from_amount": 250001, "to_amount": 500000, "rate": 19},
		{"from_amount": 500001, "to_amount": 1000000, "rate": 30},
		{"from_amount": 1000001, "to_amount": 0, "rate": 40},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_benin_salary_components():
	"""Create Benin statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "ITS", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNSS Pension Employee", "salary_component_abbr": "CNSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNSS Pension Employer", "salary_component_abbr": "CNSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_benin_income_tax_slab():
	"""Create Benin ITS Income Tax Slab (monthly bands, CGI 2026)."""
	_create_income_tax_slab(slab_name="Benin ITS 2026", currency="XOF", bands=[
		{"from_amount": 0, "to_amount": 60000, "rate": 0},
		{"from_amount": 60001, "to_amount": 150000, "rate": 10},
		{"from_amount": 150001, "to_amount": 250000, "rate": 15},
		{"from_amount": 250001, "to_amount": 500000, "rate": 19},
		{"from_amount": 500001, "to_amount": 1000000, "rate": 30},
		{"from_amount": 1000001, "to_amount": 0, "rate": 40},
	])


def setup_togo():
	"""Set up Togo payroll components, Income Tax Slab, and default settings (with INAM 5%/5%)."""
	_create_togo_settings()
	_create_togo_salary_components()
	_create_togo_income_tax_slab()
	_create_salary_structure("Togo Payroll Template", "XOF", ["PIT", "CNSS Employee", "CNSS Employer", "INAM Employee", "INAM Employer"])


def _create_togo_settings():
	"""Create Togo Payroll Settings (CNSS/INAM/CGI 2026)."""
	doc = frappe.get_doc("Togo Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.cnss_employee_rate = 4
	doc.cnss_employer_rate = 17.5
	doc.cnss_ceiling = 500000
	doc.minimum_wage = 52500
	doc.inam_employee_rate = 5
	doc.inam_employer_rate = 5
	doc.pit_threshold = 900000
	for band in [
		{"from_amount": 0, "to_amount": 900000, "rate": 0},
		{"from_amount": 900001, "to_amount": 3000000, "rate": 3},
		{"from_amount": 3000001, "to_amount": 6000000, "rate": 10},
		{"from_amount": 6000001, "to_amount": 9000000, "rate": 15},
		{"from_amount": 9000001, "to_amount": 12000000, "rate": 20},
		{"from_amount": 12000001, "to_amount": 15000000, "rate": 25},
		{"from_amount": 15000001, "to_amount": 20000000, "rate": 30},
		{"from_amount": 20000001, "to_amount": 0, "rate": 35},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def _create_togo_salary_components():
	"""Create Togo statutory salary components."""
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "IRPP", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "CNSS Employee", "salary_component_abbr": "CNSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "CNSS Employer", "salary_component_abbr": "CNSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "INAM Employee", "salary_component_abbr": "INAMe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "INAM Employer", "salary_component_abbr": "INAMr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)


def _create_togo_income_tax_slab():
	"""Create Togo IRPP Income Tax Slab (annual bands, CGI Art.74)."""
	_create_income_tax_slab(slab_name="Togo IRPP 2026", currency="XOF", bands=[
		{"from_amount": 0, "to_amount": 900000, "rate": 0},
		{"from_amount": 900001, "to_amount": 3000000, "rate": 3},
		{"from_amount": 3000001, "to_amount": 6000000, "rate": 10},
		{"from_amount": 6000001, "to_amount": 9000000, "rate": 15},
		{"from_amount": 9000001, "to_amount": 12000000, "rate": 20},
		{"from_amount": 12000001, "to_amount": 15000000, "rate": 25},
		{"from_amount": 15000001, "to_amount": 20000000, "rate": 30},
		{"from_amount": 20000001, "to_amount": 0, "rate": 35},
	])


def setup_seychelles():
	"""Set up Seychelles payroll (PAYE monthly bands, SSCR employer 5%)."""
	_create_seychelles_settings()
	for comp_data in [
		{"salary_component": "PAYE", "salary_component_abbr": "PAYE", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "Social Security Employer", "salary_component_abbr": "SSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)
	_create_income_tax_slab(slab_name="Seychelles PAYE 2026", currency="SCR", bands=[
		{"from_amount": 0, "to_amount": 8555.50, "rate": 0},
		{"from_amount": 8555.50, "to_amount": 10027.75, "rate": 15},
		{"from_amount": 10027.75, "to_amount": 13630, "rate": 20},
		{"from_amount": 13630, "to_amount": 0, "rate": 30},
	])
	_create_salary_structure("Seychelles Payroll Template", "SCR", ["PAYE", "Social Security Employer"])


def _create_seychelles_settings():
	"""Create Seychelles Payroll Settings (SRC 2026)."""
	doc = frappe.get_doc("Seychelles Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.tax_free_threshold = 8555.50
	doc.social_security_rate = 5
	doc.social_security_ceiling = 15000
	for band in [
		{"from_amount": 0, "to_amount": 8555.50, "rate": 0},
		{"from_amount": 8555.50, "to_amount": 10027.75, "rate": 15},
		{"from_amount": 10027.75, "to_amount": 13630, "rate": 20},
		{"from_amount": 13630, "to_amount": 0, "rate": 30},
	]:
		doc.append("paye_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_lesotho():
	"""Set up Lesotho payroll (PAYE annual bands + M11,640 tax credit)."""
	_create_lesotho_settings()
	_upsert_salary_component({"salary_component": "PAYE", "salary_component_abbr": "PAYE", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0})
	_create_income_tax_slab(slab_name="Lesotho PAYE 2026", currency="LSL", bands=[
		{"from_amount": 0, "to_amount": 74040, "rate": 20},
		{"from_amount": 74040, "to_amount": 0, "rate": 30},
	])
	_create_salary_structure("Lesotho Payroll Template", "LSL", ["PAYE"])


def _create_lesotho_settings():
	"""Create Lesotho Payroll Settings (LRA 2026)."""
	doc = frappe.get_doc("Lesotho Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.tax_credit_annual = 11640
	for band in [
		{"from_amount": 0, "to_amount": 74040, "rate": 20},
		{"from_amount": 74040, "to_amount": 0, "rate": 30},
	]:
		doc.append("paye_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_eswatini():
	"""Set up Eswatini payroll (PAYE annual bands, ENPF 5%/5% capped, SDL 1%)."""
	_create_eswatini_settings()
	for comp_data in [
		{"salary_component": "PAYE", "salary_component_abbr": "PAYE", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "ENPF Employee", "salary_component_abbr": "ENPFe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "ENPF Employer", "salary_component_abbr": "ENPFr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "Skills Development Levy", "salary_component_abbr": "SDL", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)
	_create_income_tax_slab(slab_name="Eswatini PAYE 2026", currency="SZL", bands=[
		{"from_amount": 0, "to_amount": 100000, "rate": 20},
		{"from_amount": 100000, "to_amount": 150000, "rate": 25},
		{"from_amount": 150000, "to_amount": 200000, "rate": 30},
		{"from_amount": 200000, "to_amount": 0, "rate": 33},
	])
	_create_salary_structure("Eswatini Payroll Template", "SZL", ["PAYE", "ENPF Employee", "ENPF Employer", "Skills Development Levy"])


def _create_eswatini_settings():
	"""Create Eswatini Payroll Settings (ERS/ENPF 2025/26)."""
	doc = frappe.get_doc("Eswatini Payroll Settings")
	if doc.paye_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.tax_rebate_annual = 8200
	doc.enpf_rate = 5
	doc.enpf_cap_total = 400
	doc.sdl_rate = 1
	for band in [
		{"from_amount": 0, "to_amount": 100000, "rate": 20},
		{"from_amount": 100000, "to_amount": 150000, "rate": 25},
		{"from_amount": 150000, "to_amount": 200000, "rate": 30},
		{"from_amount": 200000, "to_amount": 0, "rate": 33},
	]:
		doc.append("paye_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_guinea():
	"""Set up Guinea payroll (INSS pension/family/injury, AMO, PIT 0-40%)."""
	_create_guinea_settings()
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "IRPP", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "INSS Pension Employee", "salary_component_abbr": "INSSPe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "INSS Pension Employer", "salary_component_abbr": "INSSPr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "INSS Family Allowances", "salary_component_abbr": "INSSFa", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "Work Injury Insurance", "salary_component_abbr": "WII", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
		{"salary_component": "AMO Health Employee", "salary_component_abbr": "AMOe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "AMO Health Employer", "salary_component_abbr": "AMOr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)
	_create_income_tax_slab(slab_name="Guinea PIT 2026", currency="GNF", bands=[
		{"from_amount": 0, "to_amount": 1200000, "rate": 0},
		{"from_amount": 1200000, "to_amount": 3000000, "rate": 5},
		{"from_amount": 3000000, "to_amount": 6000000, "rate": 12},
		{"from_amount": 6000000, "to_amount": 12000000, "rate": 20},
		{"from_amount": 12000000, "to_amount": 24000000, "rate": 30},
		{"from_amount": 24000000, "to_amount": 0, "rate": 40},
	])
	_create_salary_structure("Guinea Payroll Template", "GNF", ["PIT", "INSS Pension Employee", "INSS Pension Employer", "INSS Family Allowances", "Work Injury Insurance", "AMO Health Employee", "AMO Health Employer"])


def _create_guinea_settings():
	"""Create Guinea Payroll Settings (INSS/DGI). minimum_wage is CONFIRM-NEEDED (SMIG)."""
	doc = frappe.get_doc("Guinea Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.inss_pension_employee_rate = 2.5
	doc.inss_pension_employer_rate = 5
	doc.inss_family_rate = 3
	doc.work_injury_risk_class = 1
	doc.amo_employee_rate = 1.5
	doc.amo_employer_rate = 1.5
	doc.minimum_wage = 550000
	for band in [
		{"from_amount": 0, "to_amount": 1200000, "rate": 0},
		{"from_amount": 1200000, "to_amount": 3000000, "rate": 5},
		{"from_amount": 3000000, "to_amount": 6000000, "rate": 12},
		{"from_amount": 6000000, "to_amount": 12000000, "rate": 20},
		{"from_amount": 12000000, "to_amount": 24000000, "rate": 30},
		{"from_amount": 24000000, "to_amount": 0, "rate": 40},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_guinea_bissau():
	"""Set up Guinea-Bissau payroll (INSS 8%/14%, IRPS 1-20% 9-band)."""
	_create_guinea_bissau_settings()
	for comp_data in [
		{"salary_component": "PIT", "salary_component_abbr": "IRPS", "type": "Deduction", "variable_based_on_taxable_salary": 1, "exempted_from_income_tax": 0},
		{"salary_component": "INSS Employee", "salary_component_abbr": "INSSe", "type": "Deduction", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 1},
		{"salary_component": "INSS Employer", "salary_component_abbr": "INSSr", "type": "Employer Contribution", "variable_based_on_taxable_salary": 0, "exempted_from_income_tax": 0},
	]:
		_upsert_salary_component(comp_data)
	_create_income_tax_slab(slab_name="Guinea-Bissau IRPS 2026", currency="XOF", bands=[
		{"from_amount": 0, "to_amount": 500000, "rate": 1},
		{"from_amount": 500000, "to_amount": 1000000, "rate": 6},
		{"from_amount": 1000000, "to_amount": 2500000, "rate": 8},
		{"from_amount": 2500000, "to_amount": 3600000, "rate": 10},
		{"from_amount": 3600000, "to_amount": 4806000, "rate": 12},
		{"from_amount": 4806000, "to_amount": 9000000, "rate": 14},
		{"from_amount": 9000000, "to_amount": 13200000, "rate": 16},
		{"from_amount": 13200000, "to_amount": 18000000, "rate": 18},
		{"from_amount": 18000000, "to_amount": 0, "rate": 20},
	])
	_create_salary_structure("Guinea-Bissau Payroll Template", "XOF", ["PIT", "INSS Employee", "INSS Employer"])


def _create_guinea_bissau_settings():
	"""Create Guinea-Bissau Payroll Settings (INSS/CGI)."""
	doc = frappe.get_doc("Guinea-Bissau Payroll Settings")
	if doc.pit_bands:
		return
	doc.enabled = 1
	doc.effective_from = "2026-01-01"
	doc.inss_employee_rate = 8
	doc.inss_employer_rate = 14
	doc.inss_ceiling = 0
	doc.minimum_wage = 45000
	for band in [
		{"from_amount": 0, "to_amount": 500000, "rate": 1},
		{"from_amount": 500000, "to_amount": 1000000, "rate": 6},
		{"from_amount": 1000000, "to_amount": 2500000, "rate": 8},
		{"from_amount": 2500000, "to_amount": 3600000, "rate": 10},
		{"from_amount": 3600000, "to_amount": 4806000, "rate": 12},
		{"from_amount": 4806000, "to_amount": 9000000, "rate": 14},
		{"from_amount": 9000000, "to_amount": 13200000, "rate": 16},
		{"from_amount": 13200000, "to_amount": 18000000, "rate": 18},
		{"from_amount": 18000000, "to_amount": 0, "rate": 20},
	]:
		doc.append("pit_bands", band)
	doc.flags.ignore_permissions = True
	doc.save()


def setup_somalia():
	"""Somalia has no mandatory statutory payroll deductions (documented no-op)."""
	doc = frappe.get_doc("Somalia Payroll Settings")
	doc.enabled = 1
	if not doc.effective_from:
		doc.effective_from = "2026-01-01"
	doc.flags.ignore_permissions = True
	doc.save()


def setup_south_sudan():
	"""South Sudan has no standardized statutory payroll deductions (documented no-op)."""
	doc = frappe.get_doc("South Sudan Payroll Settings")
	doc.enabled = 1
	if not doc.effective_from:
		doc.effective_from = "2026-01-01"
	doc.flags.ignore_permissions = True
	doc.save()


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
	with open(template_path) as f:  # nosemgrep: frappe-security-file-traversal
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
		link_to = item_data.get("link_to", "")
		link_type = item_data.get("link_type", "")
		if link_to and link_type and not frappe.db.exists(link_type, link_to):
			continue  # skip links whose target report/doctype isn't installed
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
		"Egypt IT 2025", "Ghana PAYE 2025",
		"Botswana PAYE 2025", "Morocco IR 2025",
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
