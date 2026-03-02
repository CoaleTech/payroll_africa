from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class TanzaniaCalculator(BaseCalculator):
	"""Tanzania statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. NSSF Employee (pre-PAYE, exempted_from_income_tax=1)
		nssf_emp = gross * (flt(self.settings.nssf_employee_rate) / 100)
		results["NSSF Employee TZ"] = {"amount": nssf_emp, "is_employer_only": False}

		# 2. NSSF Employer (statistical)
		nssf_empr = gross * (flt(self.settings.nssf_employer_rate) / 100)
		results["NSSF Employer TZ"] = {"amount": nssf_empr, "is_employer_only": True}

		# 3. SDL - Skills Development Levy (employer only)
		sdl = gross * (flt(self.settings.sdl_rate) / 100)
		results["SDL"] = {"amount": sdl, "is_employer_only": True}

		# 4. WCF - Workers Compensation Fund (employer only)
		wcf = gross * (flt(self.settings.wcf_rate) / 100)
		results["WCF"] = {"amount": wcf, "is_employer_only": True}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results
