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
	# Tier 2 — High priority
	"Algeria": "payroll_africa.calculators.algeria.AlgeriaCalculator",
	"Senegal": "payroll_africa.calculators.senegal.SenegalCalculator",
	"Cameroon": "payroll_africa.calculators.cameroon.CameroonCalculator",
	"Mauritius": "payroll_africa.calculators.mauritius.MauritiusCalculator",
	"Zimbabwe": "payroll_africa.calculators.zimbabwe.ZimbabweCalculator",
	"Mali": "payroll_africa.calculators.mali.MaliCalculator",
	# Tier 3 — Medium priority
	"Niger": "payroll_africa.calculators.niger.NigerCalculator",
	"Burkina Faso": "payroll_africa.calculators.burkina_faso.BurkinaFasoCalculator",
	"Benin": "payroll_africa.calculators.benin.BeninCalculator",
	"Gabon": "payroll_africa.calculators.gabon.GabonCalculator",
	"Congo": "payroll_africa.calculators.congo.CongoCalculator",
	"Guinea": "payroll_africa.calculators.guinea.GuineaCalculator",
	"Togo": "payroll_africa.calculators.togo.TogoCalculator",
	"Seychelles": "payroll_africa.calculators.seychelles.SeychellesCalculator",
	# Tier 4 — Remaining countries
	"Cabo Verde": "payroll_africa.calculators.cabo_verde.CaboVerdeCalculator",
	"Central African Republic": "payroll_africa.calculators.central_african_republic.CentralAfricanRepublicCalculator",
	"Chad": "payroll_africa.calculators.chad.ChadCalculator",
	"Comoros": "payroll_africa.calculators.comoros.ComorosCalculator",
	"Djibouti": "payroll_africa.calculators.djibouti.DjiboutiCalculator",
	"Equatorial Guinea": "payroll_africa.calculators.equatorial_guinea.EquatorialGuineaCalculator",
	"Eritrea": "payroll_africa.calculators.eritrea.EritreaCalculator",
	"Eswatini": "payroll_africa.calculators.eswatini.EswatiniCalculator",
	"Gambia": "payroll_africa.calculators.gambia.GambiaCalculator",
	"Guinea-Bissau": "payroll_africa.calculators.guinea_bissau.GuineaBissauCalculator",
	"Lesotho": "payroll_africa.calculators.lesotho.LesothoCalculator",
	"Liberia": "payroll_africa.calculators.liberia.LiberiaCalculator",
	"Libya": "payroll_africa.calculators.libya.LibyaCalculator",
	"Mauritania": "payroll_africa.calculators.mauritania.MauritaniaCalculator",
	"Sao Tome and Principe": "payroll_africa.calculators.sao_tome_principe.SaoTomePrincipeCalculator",
	"Sierra Leone": "payroll_africa.calculators.sierra_leone.SierraLeoneCalculator",
	"Somalia": "payroll_africa.calculators.somalia.SomaliaCalculator",
	"South Sudan": "payroll_africa.calculators.south_sudan.SouthSudanCalculator",
	"Sudan": "payroll_africa.calculators.sudan.SudanCalculator",
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
	"Algeria": "Algeria Payroll Settings",
	"Senegal": "Senegal Payroll Settings",
	"Cameroon": "Cameroon Payroll Settings",
	"Mauritius": "Mauritius Payroll Settings",
	"Zimbabwe": "Zimbabwe Payroll Settings",
	"Mali": "Mali Payroll Settings",
	"Niger": "Niger Payroll Settings",
	"Burkina Faso": "Burkina Faso Payroll Settings",
	"Benin": "Benin Payroll Settings",
	"Gabon": "Gabon Payroll Settings",
	"Congo": "Congo Payroll Settings",
	"Guinea": "Guinea Payroll Settings",
	"Togo": "Togo Payroll Settings",
	"Seychelles": "Seychelles Payroll Settings",
	"Cabo Verde": "Cabo Verde Payroll Settings",
	"Central African Republic": "Central African Republic Payroll Settings",
	"Chad": "Chad Payroll Settings",
	"Comoros": "Comoros Payroll Settings",
	"Djibouti": "Djibouti Payroll Settings",
	"Equatorial Guinea": "Equatorial Guinea Payroll Settings",
	"Eritrea": "Eritrea Payroll Settings",
	"Eswatini": "Eswatini Payroll Settings",
	"Gambia": "Gambia Payroll Settings",
	"Guinea-Bissau": "Guinea-Bissau Payroll Settings",
	"Lesotho": "Lesotho Payroll Settings",
	"Liberia": "Liberia Payroll Settings",
	"Libya": "Libya Payroll Settings",
	"Mauritania": "Mauritania Payroll Settings",
	"Sao Tome and Principe": "Sao Tome and Principe Payroll Settings",
	"Sierra Leone": "Sierra Leone Payroll Settings",
	"Somalia": "Somalia Payroll Settings",
	"South Sudan": "South Sudan Payroll Settings",
	"Sudan": "Sudan Payroll Settings",
}

VALID_SUFFIXES = {
	"UG", "TZ", "RW", "BI", "ZM", "MW", "CD", "NG", "MZ", "AO", "GH", "ET", "ZA", "EG", "BW", "MA", "CI", "TN", "NA", "MG",
	"DZ", "SN", "CM", "MU", "ZW", "ML", "NE", "BF", "BJ", "GA", "CG", "GN", "TG", "SC",
	"CV", "CF", "TD", "KM", "DJ", "GQ", "ER", "SZ", "GM", "GW", "LS", "LR", "LY", "MR", "ST", "SL", "SO", "SS", "SD",
	""
}


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
