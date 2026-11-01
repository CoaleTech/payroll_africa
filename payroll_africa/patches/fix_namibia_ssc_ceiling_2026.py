import frappe
from frappe.utils import flt


# Old seeded PAYE band fingerprint (from_amount, to_amount, rate, base_tax)
_OLD_BANDS = [
	(0, 100000, 0, 0),
	(100001, 250000, 18, 0),
	(250001, 500000, 25, 27000),
	(500001, 750000, 28, 89500),
	(750001, 1000000, 30, 159500),
	(1000001, 1500000, 32, 234500),
	(1500001, 0, 37, 394500),
]

_NEW_BANDS = [
	{"from_amount": 0, "to_amount": 100000, "rate": 0, "base_tax": 0},
	{"from_amount": 100001, "to_amount": 150000, "rate": 18, "base_tax": 0},
	{"from_amount": 150001, "to_amount": 350000, "rate": 25, "base_tax": 9000},
	{"from_amount": 350001, "to_amount": 550000, "rate": 28, "base_tax": 59000},
	{"from_amount": 550001, "to_amount": 850000, "rate": 30, "base_tax": 115000},
	{"from_amount": 850001, "to_amount": 1550000, "rate": 32, "base_tax": 205000},
	{"from_amount": 1550001, "to_amount": 0, "rate": 37, "base_tax": 429000},
]


def execute():
	"""Namibia: update SSC annual ceiling to NAD 150,000 (N$12,500/month, effective 1 Sep 2026)
	and replace seeded PAYE bands with 2025/26 NamRA schedule.

	Sources:
	  - Deloitte Namibia tax alert 25 Aug 2026 + Sage Namibia statutory update Aug 2026
	  - PwC Worldwide Tax Summaries Namibia (reviewed Jul 2026)

	Only corrects values that are still at the old defaults (108,000 or 132,000 for ceiling;
	replaces band table only when it exactly matches the old seeded bands).
	"""
	if not frappe.db.exists("DocType", "Namibia Payroll Settings"):
		return

	doc_name = "Namibia Payroll Settings"

	# Update SSC ceiling: rewrite 108,000 or 132,000 → 150,000
	current_ceiling = frappe.db.get_value("Namibia Payroll Settings", doc_name, "ssc_annual_ceiling")
	if current_ceiling is not None and flt(current_ceiling) in (108000, 132000):
		frappe.db.set_value("Namibia Payroll Settings", doc_name, "ssc_annual_ceiling", 150000)

	# Replace PAYE bands only if they still match the old seeded 7-band 2024 schedule
	existing = frappe.get_all(
		"Namibia PAYE Band",
		filters={"parenttype": "Namibia Payroll Settings", "parent": doc_name},
		fields=["from_amount", "to_amount", "rate", "base_tax"],
		order_by="idx asc",
	)
	if len(existing) == len(_OLD_BANDS):
		matches = all(
			flt(r.from_amount) == old[0]
			and flt(r.to_amount) == old[1]
			and flt(r.rate) == old[2]
			and flt(r.base_tax) == old[3]
			for r, old in zip(existing, _OLD_BANDS)
		)
		if matches:
			doc = frappe.get_doc("Namibia Payroll Settings")
			doc.paye_bands = []
			for band in _NEW_BANDS:
				doc.append("paye_bands", band)
			doc.flags.ignore_permissions = True
			doc.save()
