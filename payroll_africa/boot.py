import frappe


# Maps country name (as used in Employee.payroll_country / Company.country)
# to the checkbox fieldname in Payroll Africa Settings.
COUNTRY_FIELD_MAP = {
	"Kenya": "enable_kenya",
	"Uganda": "enable_uganda",
	"Tanzania": "enable_tanzania",
	"Rwanda": "enable_rwanda",
	"Burundi": "enable_burundi",
	"Zambia": "enable_zambia",
	"Malawi": "enable_malawi",
	"Congo, The Democratic Republic of the": "enable_drc",
	"Nigeria": "enable_nigeria",
	"Mozambique": "enable_mozambique",
	"Angola": "enable_angola",
	"Ghana": "enable_ghana",
	"Ethiopia": "enable_ethiopia",
	"South Africa": "enable_south_africa",
	"Egypt": "enable_egypt",
	"Botswana": "enable_botswana",
	"Morocco": "enable_morocco",
	"Ivory Coast": "enable_ivory_coast",
	"Tunisia": "enable_tunisia",
	"Namibia": "enable_namibia",
	"Madagascar": "enable_madagascar",
}


@frappe.whitelist()
def get_enabled_countries():
	"""Return list of enabled country names from Payroll Africa Settings."""
	settings = frappe.get_cached_doc("Payroll Africa Settings")
	if not settings.enabled:
		return []
	return [
		country for country, field in COUNTRY_FIELD_MAP.items()
		if settings.get(field)
	]


BOOT_CACHE_KEY = "payroll_africa_enabled_countries"


def extend_bootinfo(bootinfo):
	"""Add enabled countries to boot info for client-side filtering."""
	cached = frappe.cache().get_value(BOOT_CACHE_KEY)
	if cached is None:
		cached = get_enabled_countries()
		frappe.cache().set_value(BOOT_CACHE_KEY, cached, expires_in_sec=3600)
	bootinfo.payroll_africa_enabled_countries = cached
