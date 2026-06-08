import frappe

COUNTRY_MAP = {
	"Kenya": "payroll_africa.calculators.kenya.KenyaCalculator",
	"Uganda": "payroll_africa.calculators.uganda.UgandaCalculator",
	"Tanzania": "payroll_africa.calculators.tanzania.TanzaniaCalculator",
	"Rwanda": "payroll_africa.calculators.rwanda.RwandaCalculator",
	"Burundi": "payroll_africa.calculators.burundi.BurundiCalculator",
	"Zambia": "payroll_africa.calculators.zambia.ZambiaCalculator",
	"Malawi": "payroll_africa.calculators.malawi.MalawiCalculator",
	"Congo, The Democratic Republic of the": "payroll_africa.calculators.drc.DRCCalculator",
	"Nigeria": "payroll_africa.calculators.nigeria.NigeriaCalculator",
	"Angola": "payroll_africa.calculators.angola.AngolaCalculator",
	"Mozambique": "payroll_africa.calculators.mozambique.MozambiqueCalculator",
	"Ghana": "payroll_africa.calculators.ghana.GhanaCalculator",
	"Ethiopia": "payroll_africa.calculators.ethiopia.EthiopiaCalculator",
	"South Africa": "payroll_africa.calculators.south_africa.SouthAfricaCalculator",
	"Egypt": "payroll_africa.calculators.egypt.EgyptCalculator",
	"Botswana": "payroll_africa.calculators.botswana.BotswanaCalculator",
	"Morocco": "payroll_africa.calculators.morocco.MoroccoCalculator",
	"Ivory Coast": "payroll_africa.calculators.ivory_coast.IvoryCoastCalculator",
	"Tunisia": "payroll_africa.calculators.tunisia.TunisiaCalculator",
	"Namibia": "payroll_africa.calculators.namibia.NamibiaCalculator",
	"Madagascar": "payroll_africa.calculators.madagascar.MadagascarCalculator",
}

SETTINGS_MAP = {
	"Kenya": "Kenya Payroll Settings",
	"Uganda": "Uganda Payroll Settings",
	"Tanzania": "Tanzania Payroll Settings",
	"Rwanda": "Rwanda Payroll Settings",
	"Burundi": "Burundi Payroll Settings",
	"Zambia": "Zambia Payroll Settings",
	"Malawi": "Malawi Payroll Settings",
	"Congo, The Democratic Republic of the": "DRC Payroll Settings",
	"Nigeria": "Nigeria Payroll Settings",
	"Angola": "Angola Payroll Settings",
	"Mozambique": "Mozambique Payroll Settings",
	"Ghana": "Ghana Payroll Settings",
	"Ethiopia": "Ethiopia Payroll Settings",
	"South Africa": "South Africa Payroll Settings",
	"Egypt": "Egypt Payroll Settings",
	"Botswana": "Botswana Payroll Settings",
	"Morocco": "Morocco Payroll Settings",
	"Ivory Coast": "Ivory Coast Payroll Settings",
	"Tunisia": "Tunisia Payroll Settings",
	"Namibia": "Namibia Payroll Settings",
	"Madagascar": "Madagascar Payroll Settings",
}

VALID_SUFFIXES = {"UG", "TZ", "RW", "BI", "ZM", "MW", "CD", "NG", "MZ", "AO", "GH", "ET", "ZA", "EG", "BW", "MA", "CI", "TN", "NA", "MG", ""}


def is_supported_country(country: str) -> bool:
	return country in COUNTRY_MAP


def get_supported_countries() -> list[str]:
	return sorted(COUNTRY_MAP.keys())


def get_calculator(country):
	if country not in COUNTRY_MAP:
		return None
	settings = get_country_settings(country)
	if not settings:
		# Return calculator with empty settings so hardcoded defaults apply
		settings = frappe._dict()
	calculator_class = frappe.get_attr(COUNTRY_MAP[country])
	return calculator_class(settings)


def get_country_settings(country):
	"""Load country-specific payroll settings."""
	doctype = SETTINGS_MAP.get(country)
	if not doctype:
		return None
	try:
		return frappe.get_cached_doc(doctype)
	except frappe.DoesNotExistError:
		return None
