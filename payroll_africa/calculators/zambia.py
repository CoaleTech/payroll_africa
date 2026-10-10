from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class ZambiaCalculator(BaseCalculator):
	"""Zambia statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. NAPSA Employee (% of gross, capped; not deductible for PAYE since 2025)
		napsa_cap = flt(self.settings.napsa_cap)
		napsa_gross = min(gross, napsa_cap) if napsa_cap else gross
		napsa_emp = napsa_gross * (flt(self.settings.napsa_employee_rate) / 100)
		results["NAPSA Employee ZM"] = {"amount": napsa_emp, "is_employer_only": False}

		# 2. NAPSA Employer (statistical, capped)
		napsa_empr = napsa_gross * (flt(self.settings.napsa_employer_rate) / 100)
		results["NAPSA Employer ZM"] = {"amount": napsa_empr, "is_employer_only": True}

		# 3-4. NHIMA: % of BASIC salary only (SI 63 of 2019, Third Schedule), no cap
		basic = self.get_basic_pay(salary_slip)
		nhima_emp = basic * (flt(self.settings.nhima_employee_rate) / 100)
		results["NHIMA Employee ZM"] = {"amount": nhima_emp, "is_employer_only": False}

		nhima_empr = basic * (flt(self.settings.nhima_employer_rate) / 100)
		results["NHIMA Employer ZM"] = {"amount": nhima_empr, "is_employer_only": True}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results
