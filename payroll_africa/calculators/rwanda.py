from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class RwandaCalculator(BaseCalculator):
	"""Rwanda statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. Pension Employee (pre-PAYE, exempted_from_income_tax=1)
		pension_emp = gross * (flt(self.settings.pension_employee_rate) / 100)
		results["Pension Employee RW"] = {"amount": pension_emp, "is_employer_only": False}

		# 2. Pension Employer (statistical)
		pension_empr = gross * (flt(self.settings.pension_employer_rate) / 100)
		results["Pension Employer RW"] = {"amount": pension_empr, "is_employer_only": True}

		# 3. Maternity Employee
		maternity_emp = gross * (flt(self.settings.maternity_employee_rate) / 100)
		results["Maternity Employee RW"] = {"amount": maternity_emp, "is_employer_only": False}

		# 4. Maternity Employer (statistical)
		maternity_empr = gross * (flt(self.settings.maternity_employer_rate) / 100)
		results["Maternity Employer RW"] = {"amount": maternity_empr, "is_employer_only": True}

		# 5. CBHI (employee)
		cbhi = gross * (flt(self.settings.cbhi_rate) / 100)
		results["CBHI RW"] = {"amount": cbhi, "is_employer_only": False}

		# 6. Occupational Hazards (employer only)
		occ_hazards = gross * (flt(self.settings.occupational_hazards_rate) / 100)
		results["Occupational Hazards RW"] = {"amount": occ_hazards, "is_employer_only": True}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results
