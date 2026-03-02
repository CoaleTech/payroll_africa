import frappe

_calculators = {}
_country_map = {
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
}

_settings_map = {
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
}


def get_calculator(country):
	"""Get cached calculator instance for a country."""
	if country not in _country_map:
		return None

	if country not in _calculators:
		settings = get_country_settings(country)
		if not settings:
			return None
		calculator_class = frappe.get_attr(_country_map[country])
		_calculators[country] = calculator_class(settings)

	return _calculators[country]


def get_country_settings(country):
	"""Load country-specific payroll settings."""
	doctype = _settings_map.get(country)
	if not doctype:
		return None
	try:
		return frappe.get_cached_doc(doctype)
	except frappe.DoesNotExistError:
		return None


def clear_cache():
	"""Clear calculator cache (called when settings change)."""
	_calculators.clear()
