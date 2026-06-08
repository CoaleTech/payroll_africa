import frappe
from frappe import _


def notify_rate_review():
	"""Notify Payroll Managers to review statutory rates at the start of each year."""
	from payroll_africa.boot import get_enabled_countries

	countries = get_enabled_countries()
	if not countries:
		return

	recipients = frappe.get_all(
		"Has Role",
		filters={"role": "Payroll Manager", "parenttype": "User"},
		pluck="parent",
	)
	if not recipients:
		return

	country_list = ", ".join(countries)
	for user in recipients:
		frappe.sendmail(
			recipients=[user],
			subject=_("Action Required: Review Payroll Africa Statutory Rates"),
			message=_(
				"A new year has started. Please review and update statutory rates for: {0}."
			).format(country_list),
			delayed=False,
		)
