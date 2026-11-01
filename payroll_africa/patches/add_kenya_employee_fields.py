import frappe


def execute():
	"""Add Kenya Statutory IDs section and fields to Employee DocType.

	Creates: ke_statutory_section (Section Break), tax_id (KRA PIN),
	national_id, ke_cb (Column Break), nssf_no.
	These are needed by nssf_remittance, shif_remittance, p10_monthly_tax_return,
	and housing_levy_return reports.
	"""
	from payroll_africa.setup import _setup_custom_fields

	_setup_custom_fields()
	frappe.clear_cache(doctype="Employee")
