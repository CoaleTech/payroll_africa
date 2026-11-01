import frappe


def execute():
	"""Fix Djibouti and Eritrea payroll settings written with wrong DocType JSON defaults.

	The original DocType JSON carried placeholder defaults (4/14/0 for Djibouti;
	4/10/0 for Eritrea) that were overridden in setup — but only on the first run.
	Sites already configured retained the stale values from the DocType form.

	Djibouti corrections (ISSA 2024, health+pension combined):
	  cnss_employee_rate: 4 → 2
	  cnss_employer_rate: 14 → 5
	  cnss_ceiling:        0 → 400,000 DJF/month
	  pit_threshold:       0 → 240,000 DJF/month

	Eritrea corrections (NICE 2024):
	  nice_employee_rate: 4 → 6
	  nice_employer_rate: 10 → 6
	  tax_free_threshold:  0 → 800 ERN/month
	"""
	# Djibouti
	doc_dj = frappe.get_doc("Djibouti Payroll Settings")
	if doc_dj.cnss_employee_rate == 4:
		doc_dj.cnss_employee_rate = 2
		doc_dj.cnss_employer_rate = 5
		doc_dj.cnss_ceiling = 400000
		doc_dj.pit_threshold = 240000
		doc_dj.flags.ignore_permissions = True
		doc_dj.save()

	# Eritrea
	doc_er = frappe.get_doc("Eritrea Payroll Settings")
	if doc_er.nice_employee_rate == 4:
		doc_er.nice_employee_rate = 6
		doc_er.nice_employer_rate = 6
		doc_er.tax_free_threshold = 800
		doc_er.flags.ignore_permissions = True
		doc_er.save()
