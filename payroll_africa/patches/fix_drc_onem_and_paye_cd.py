import frappe
from frappe.utils import flt


def execute():
	"""DRC: correct ONEM rate (0.5 → 0.2) and disable PAYE CD taxable-salary link.

	The setup seed previously used onem_rate=0.5 (Ministerial Order reference) while the
	DocType default is 0.2.  The PAYE CD component had variable_based_on_taxable_salary=1
	which caused HRMS to double-compute IPR — the calculator now handles it directly.
	"""
	# 1. Fix ONEM rate if it is still at the wrong seed value (0.5%)
	onem_rate = frappe.db.get_single_value("DRC Payroll Settings", "onem_rate")
	if flt(onem_rate) == 0.5:
		frappe.db.set_single_value("DRC Payroll Settings", "onem_rate", 0.2)

	# 2. Disable PAYE CD's taxable-salary link (calculator now computes IPR via paye_bands)
	if frappe.db.exists("Salary Component", "PAYE CD"):
		if frappe.db.get_value("Salary Component", "PAYE CD", "variable_based_on_taxable_salary"):
			frappe.db.set_value(
				"Salary Component", "PAYE CD", "variable_based_on_taxable_salary", 0
			)
