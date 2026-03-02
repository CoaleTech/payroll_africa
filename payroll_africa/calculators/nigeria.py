from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class NigeriaCalculator(BaseCalculator):
	"""Nigeria statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. Pension Employee (pre-PAYE, exempted_from_income_tax=1)
		pension_emp = gross * (flt(self.settings.pension_employee_rate) / 100)
		results["Pension Employee NG"] = {"amount": pension_emp, "is_employer_only": False}

		# 2. Pension Employer (statistical)
		pension_empr = gross * (flt(self.settings.pension_employer_rate) / 100)
		results["Pension Employer NG"] = {"amount": pension_empr, "is_employer_only": True}

		# 3. NHF (employee only, pre-PAYE, exempted_from_income_tax=1)
		nhf = gross * (flt(self.settings.nhf_rate) / 100)
		results["NHF NG"] = {"amount": nhf, "is_employer_only": False}

		# 4. NHIS Employee (not pre-PAYE, exempted_from_income_tax=0)
		nhis_emp = gross * (flt(self.settings.nhis_employee_rate) / 100)
		results["NHIS Employee NG"] = {"amount": nhis_emp, "is_employer_only": False}

		# 5. NHIS Employer (statistical)
		nhis_empr = gross * (flt(self.settings.nhis_employer_rate) / 100)
		results["NHIS Employer NG"] = {"amount": nhis_empr, "is_employer_only": True}

		# 6. NSITF (employer only)
		nsitf = gross * (flt(self.settings.nsitf_rate) / 100)
		results["NSITF NG"] = {"amount": nsitf, "is_employer_only": True}

		# 7. ITF (employer only)
		itf = gross * (flt(self.settings.itf_rate) / 100)
		results["ITF NG"] = {"amount": itf, "is_employer_only": True}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results
