import frappe


def execute():
	"""Cameroon: fix top PIT band rate from 38.5 to 35 (pre-CAC base rate).

	The seeded band stored 38.5% as the rate but _apply_pit_bands multiplies by the CAC
	surcharge (1.10), giving 42.35% instead of the statutory 38.5% effective rate.
	The correct base rate is 35% (35% × 1.10 = 38.5% effective).
	"""
	# Fix any Cameroon PIT Band rows where rate was incorrectly stored as 38.5
	pit_band_names = frappe.get_all(
		"Cameroon PIT Band",
		filters={"parent": "Cameroon Payroll Settings", "rate": 38.5},
		pluck="name",
	)
	for name in pit_band_names:
		frappe.db.set_value("Cameroon PIT Band", name, "rate", 35)
