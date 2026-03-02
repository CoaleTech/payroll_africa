from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class MalawiCalculator(BaseCalculator):
	"""Malawi statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. Pension Employee (pre-PAYE, exempted_from_income_tax=1)
		pension_emp = gross * (flt(self.settings.pension_employee_rate) / 100)
		results["Pension Employee MW"] = {"amount": pension_emp, "is_employer_only": False}

		# 2. Pension Employer (statistical)
		pension_empr = gross * (flt(self.settings.pension_employer_rate) / 100)
		results["Pension Employer MW"] = {"amount": pension_empr, "is_employer_only": True}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results
