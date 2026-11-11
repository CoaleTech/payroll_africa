import frappe

# (LEL, Tier I cap, Tier II cap): NSSF Act 2013 Year 4, effective February 2026.
YEAR_4 = (9000, 540, 5940)


def execute():
	"""Kenya NSSF Year 4 (Feb 2026): replace legacy Tier I/II settings.

	Tier I:  6% of gross up to LEL 9,000 -> cap 540
	Tier II: 6% of (gross - LEL) up to UEL 108,000 -> contribution cap 5,940

	Guard: only rewrites when the settings still hold a pre-Year-4 LEL
	(Year 1 6,000 / Year 2 7,000 / Year 3 8,000 or the old 18,000 default).
	"""
	doc = frappe.get_doc("Kenya Payroll Settings")
	current = (doc.nssf_tier1_upper_limit, doc.nssf_tier1_cap, doc.nssf_tier2_cap)
	if current == YEAR_4 or not 0 < (doc.nssf_tier1_upper_limit or 0) <= 18000:
		return

	doc.nssf_tier1_upper_limit, doc.nssf_tier1_cap, doc.nssf_tier2_cap = YEAR_4
	doc.flags.ignore_permissions = True
	doc.save()
