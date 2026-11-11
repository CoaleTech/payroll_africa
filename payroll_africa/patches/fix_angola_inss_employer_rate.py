import frappe
from frappe.utils import flt


def execute():
	"""Angola: set INSS employer rate to 15% (Presidential Decree 48/24) if still at
	the JSON-default value of 8 that setup never applied due to the old paye_bands guard."""
	if not frappe.db.exists("DocType", "Angola Payroll Settings"):
		return
	current = frappe.db.get_value(
		"Angola Payroll Settings", "Angola Payroll Settings", "inss_employer_rate"
	)
	if current is not None and flt(current) == 8:
		frappe.db.set_value(
			"Angola Payroll Settings", "Angola Payroll Settings", "inss_employer_rate", 15
		)
