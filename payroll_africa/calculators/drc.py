from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class DRCCalculator(BaseCalculator):
	"""DRC statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. INSS Pension Employee (pre-PAYE, exempted_from_income_tax=1)
		inss_emp = gross * (flt(self.settings.inss_pension_employee_rate) / 100)
		results["INSS Pension Employee CD"] = {"amount": inss_emp, "is_employer_only": False}

		# 2. INSS Pension Employer (statistical)
		inss_empr = gross * (flt(self.settings.inss_pension_employer_rate) / 100)
		results["INSS Pension Employer CD"] = {"amount": inss_empr, "is_employer_only": True}

		# 3. INSS Occupational Risks (employer only)
		occ_risk = gross * (flt(self.settings.inss_occupational_risks_rate) / 100)
		results["INSS Occupational Risks CD"] = {"amount": occ_risk, "is_employer_only": True}

		# 4. INSS Family Benefits (employer only)
		family = gross * (flt(self.settings.inss_family_benefits_rate) / 100)
		results["INSS Family Benefits CD"] = {"amount": family, "is_employer_only": True}

		# 5. INPP (employer only)
		inpp = gross * (flt(self.settings.inpp_rate) / 100)
		results["INPP CD"] = {"amount": inpp, "is_employer_only": True}

		# 6. ONEM (employer only)
		onem = gross * (flt(self.settings.onem_rate) / 100)
		results["ONEM CD"] = {"amount": onem, "is_employer_only": True}

		# PAYE/IPR is NOT computed here - HRMS handles it via Income Tax Slab
		return results
