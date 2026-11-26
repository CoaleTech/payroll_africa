import re

import frappe
from frappe.utils import flt

from payroll_africa.boot import COUNTRY_SUFFIX_MAP

_SUFFIXES = {s for s in COUNTRY_SUFFIX_MAP.values() if s}  # Kenya's "" suffix means no suffix

# Column buckets for employee-borne deductions across countries and apps (csf_ke: "Employee NSSF"/"SHA";
# payroll_africa: "NSSF Employee TZ", "Pension Employee MW", "INSS Employee BI", "NAPSA Employee ZM", "SHIF", "CBHI RW", ...).
_NSSF = re.compile(r"\b(NSSF|INSS|NAPSA|Pension)\b", re.I)  # pension / social security
_SHA = re.compile(r"\b(SHA|SHIF|CBHI|NHIMA|NHIS|Health)\b", re.I)  # health cover
_NITA = "NITA"  # employer-borne: shown for information, never part of net pay

COLUMNS = ("pa_gross_pay", "pa_paye", "pa_nssf", "pa_sha", "pa_nita", "pa_other_deductions", "pa_net_pay")


def add_slip_amounts(doc, method=None):
	"""Payroll Entry onload: fill the Employees grid from the entry's Salary Slips (in memory, recomputed each load)."""
	if not doc.employees or not frappe.has_permission("Salary Slip", "read"):
		return

	slips = frappe.get_all(
		"Salary Slip",
		filters={"payroll_entry": doc.name, "docstatus": ["<", 2]},
		fields=["name", "employee", "gross_pay", "net_pay"],
	)
	if not slips:
		return

	SD = frappe.qb.DocType("Salary Detail")
	details = (
		frappe.qb.from_(SD)
		.select(SD.parent, SD.parentfield, SD.salary_component, SD.amount, SD.do_not_include_in_total, SD.statistical_component)
		.where(SD.parent.isin([s.name for s in slips]) & SD.parentfield.isin(["deductions", "employer_contributions"]))
		.run(as_dict=True)
	)

	totals = summarise(slips, details)
	for row in doc.employees:
		for col, value in totals.get(row.employee, {}).items():
			row.set(col, value)


def summarise(slips, details):
	"""{employee: {column: amount}} from Salary Slip headers and their deduction/contribution rows."""
	by_slip = {}
	for d in details:
		by_slip.setdefault(d["parent"], []).append(d)

	out = {}
	for slip in slips:
		t = out.setdefault(slip["employee"], dict.fromkeys(COLUMNS, 0.0))
		t["pa_gross_pay"] += flt(slip["gross_pay"])
		t["pa_net_pay"] += flt(slip["net_pay"])
		for d in by_slip.get(slip["name"], []):
			amount = flt(d["amount"])
			base = _base(d["salary_component"])
			if base == _NITA:
				t["pa_nita"] += amount
			elif d["parentfield"] != "deductions" or d["do_not_include_in_total"] or d["statistical_component"]:
				continue  # employer-side or statistical rows do not reduce net pay
			elif base == "PAYE":
				t["pa_paye"] += amount
			elif _NSSF.search(base):
				t["pa_nssf"] += amount
			elif _SHA.search(base):
				t["pa_sha"] += amount
			else:
				t["pa_other_deductions"] += amount
	return out


def _base(component):
	"""'PAYE TZ' -> 'PAYE': drop a trailing country suffix."""
	head, _sep, tail = component.rpartition(" ")
	return head if head and tail in _SUFFIXES else component
