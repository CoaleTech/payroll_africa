import frappe


def execute():
	"""Namibia: update SSC annual ceiling from NAD 108,000 to NAD 132,000 (GN 8461, Mar 2025)
	if still at the stale JSON-default value that setup never applied."""
	if not frappe.db.exists("DocType", "Namibia Payroll Settings"):
		return
	current = frappe.db.get_value(
		"Namibia Payroll Settings", "Namibia Payroll Settings", "ssc_annual_ceiling"
	)
	if current is not None and float(current or 0) == 108000:
		frappe.db.set_value(
			"Namibia Payroll Settings", "Namibia Payroll Settings", "ssc_annual_ceiling", 132000
		)
