import frappe


def execute():
	"""Zimbabwe: set NSSA annual ceiling to USD 8,400 (USD 700/month, NSSA 2025) and
	populate the PAYE band table with the ZIMRA formula-method bands if still empty.

	Only corrects values still at the known-wrong defaults to avoid clobbering user edits.
	"""
	if not frappe.db.exists("DocType", "Zimbabwe Payroll Settings"):
		return

	current_ceiling = frappe.db.get_value(
		"Zimbabwe Payroll Settings", "Zimbabwe Payroll Settings", "nssa_annual_ceiling"
	)
	if current_ceiling is not None and float(current_ceiling or 0) == 1914360:
		frappe.db.set_value(
			"Zimbabwe Payroll Settings", "Zimbabwe Payroll Settings", "nssa_annual_ceiling", 8400
		)

	# Populate PAYE bands if the table is still empty (setup was previously blocked)
	existing_bands = frappe.get_all(
		"Zimbabwe PAYE Band",
		filters={"parenttype": "Zimbabwe Payroll Settings", "parent": "Zimbabwe Payroll Settings"},
	)
	if not existing_bands:
		doc = frappe.get_doc("Zimbabwe Payroll Settings")
		for band in [
			{"from_amount": 0,    "to_amount": 100,  "rate": 0,  "deduction": 0},
			{"from_amount": 101,  "to_amount": 300,  "rate": 20, "deduction": 20},
			{"from_amount": 301,  "to_amount": 1000, "rate": 25, "deduction": 35},
			{"from_amount": 1001, "to_amount": 2000, "rate": 30, "deduction": 85},
			{"from_amount": 2001, "to_amount": 3000, "rate": 35, "deduction": 185},
			{"from_amount": 3001, "to_amount": 0,    "rate": 40, "deduction": 335},
		]:
			doc.append("paye_bands", band)
		doc.flags.ignore_permissions = True
		doc.save()
