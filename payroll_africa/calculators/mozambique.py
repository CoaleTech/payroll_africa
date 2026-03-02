from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class MozambiqueCalculator(BaseCalculator):
	"""Mozambique statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. INSS Employee (pre-PAYE, exempted_from_income_tax=1)
		inss_emp = gross * (flt(self.settings.inss_employee_rate) / 100)
		results["INSS Employee MZ"] = {"amount": inss_emp, "is_employer_only": False}

		# 2. INSS Employer (statistical)
		inss_empr = gross * (flt(self.settings.inss_employer_rate) / 100)
		results["INSS Employer MZ"] = {"amount": inss_empr, "is_employer_only": True}

		# PAYE/IRPS is NOT computed here - HRMS handles it via Income Tax Slab
		return results
