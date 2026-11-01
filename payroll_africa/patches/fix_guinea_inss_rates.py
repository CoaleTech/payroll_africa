import frappe
from frappe.utils import flt


def execute():
	"""Guinea: correct INSS/AMO rates and minimum wage to verified 2022/2026 statutory values.

	Sources:
	  - CNSS Guinea (cnss.gov.gn/cotisations-sociales-employeurs): pension 5%/1.5%, family 6%,
	    work injury 4%, health/AMO employee 0%/employer 6.5%
	  - Decree D/2022/0270/PRG/SGG (1 June 2022): SMIG = 550,000 GNF/month
	  - Fixed ceiling: 2,500,000 GNF/month (not 8x minimum wage)

	Only rewrites values still at the known-wrong JSON defaults to avoid clobbering user edits.
	"""
	if not frappe.db.exists("DocType", "Guinea Payroll Settings"):
		return

	doc_name = "Guinea Payroll Settings"

	corrections = {
		"inss_pension_employee_rate": (2.5, 5.0),
		"inss_pension_employer_rate": (5.0, 1.5),
		"inss_family_rate": (3.0, 6.0),
		"amo_employee_rate": (1.5, 0.0),
		"amo_employer_rate": (1.5, 6.5),
		"minimum_wage": (440000, 550000),
	}

	for field, (old_val, new_val) in corrections.items():
		current = frappe.db.get_value("Guinea Payroll Settings", doc_name, field)
		if current is not None and flt(current) == old_val:
			frappe.db.set_value("Guinea Payroll Settings", doc_name, field, new_val)

	# Also correct minimum_wage if still at the code-fallback default
	current_wage = frappe.db.get_value("Guinea Payroll Settings", doc_name, "minimum_wage")
	if current_wage is not None and flt(current_wage) == 80000:
		frappe.db.set_value("Guinea Payroll Settings", doc_name, "minimum_wage", 550000)

	# Set inss_ceiling if not already set (field may not exist yet before migrate)
	try:
		current_ceiling = frappe.db.get_value("Guinea Payroll Settings", doc_name, "inss_ceiling")
		if not current_ceiling or flt(current_ceiling) == 0:
			frappe.db.set_value("Guinea Payroll Settings", doc_name, "inss_ceiling", 2500000)
	except Exception:
		pass  # field does not exist yet; migrate will add it
