import frappe
from frappe.utils import flt


def execute():
	"""Eswatini: update ENPF monthly cap to SZL 430 (E215/side, effective 1 Jan 2026)
	and seed the secondary tax rebate for employees aged 60+.

	Sources:
	  - Legal Notice 5 of 2025 via myworkpay.com 2026: total cap E430/month (E215 per side,
	    wage ceiling E4,300) effective 1 January 2026
	  - PwC Eswatini (reviewed Mar 2026) + Teamed (Oct 2026): secondary rebate E2,700/year
	    for employees aged 60 and over (total rebate E10,900/year)

	Only rewrites values still at the old known default (400 → 430).
	Adds tax_rebate_secondary if not already set.
	"""
	if not frappe.db.exists("DocType", "Eswatini Payroll Settings"):
		return

	doc_name = "Eswatini Payroll Settings"

	current_cap = frappe.db.get_value("Eswatini Payroll Settings", doc_name, "enpf_cap_total")
	if current_cap is not None and flt(current_cap) == 400:
		frappe.db.set_value("Eswatini Payroll Settings", doc_name, "enpf_cap_total", 430)

	# Add secondary rebate if missing or zero
	try:
		current_rebate = frappe.db.get_value(
			"Eswatini Payroll Settings", doc_name, "tax_rebate_secondary"
		)
		if not current_rebate or flt(current_rebate) == 0:
			frappe.db.set_value(
				"Eswatini Payroll Settings", doc_name, "tax_rebate_secondary", 2700
			)
	except Exception:
		pass  # field not yet migrated
