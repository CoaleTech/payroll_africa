from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class UgandaCalculator(BaseCalculator):
	"""Uganda statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. NSSF Employee (pre-PAYE, exempted_from_income_tax=1)
		nssf_emp = gross * (flt(self.settings.nssf_employee_rate) / 100)
		results["NSSF Employee UG"] = {"amount": nssf_emp, "is_employer_only": False}

		# 2. NSSF Employer (statistical)
		nssf_empr = gross * (flt(self.settings.nssf_employer_rate) / 100)
		results["NSSF Employer UG"] = {"amount": nssf_empr, "is_employer_only": True}

		# 3. LST (employee deduction, monthly = annual / 12)
		lst_monthly = flt(self.settings.lst_annual_amount) / 12
		results["LST"] = {"amount": lst_monthly, "is_employer_only": False}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results
