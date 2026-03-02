from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class BurundiCalculator(BaseCalculator):
	"""Burundi statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. INSS Employee (pre-PAYE, exempted_from_income_tax=1)
		inss_emp = gross * (flt(self.settings.inss_employee_rate) / 100)
		results["INSS Employee BI"] = {"amount": inss_emp, "is_employer_only": False}

		# 2. INSS Employer (statistical)
		inss_empr = gross * (flt(self.settings.inss_employer_rate) / 100)
		results["INSS Employer BI"] = {"amount": inss_empr, "is_employer_only": True}

		# 3. Work Injury (employer only, statistical)
		work_injury = gross * (flt(self.settings.work_injury_rate) / 100)
		results["Work Injury BI"] = {"amount": work_injury, "is_employer_only": True}

		# 4. Health Insurance Employee
		health_emp = gross * (flt(self.settings.health_employee_rate) / 100)
		results["Health Insurance Employee BI"] = {"amount": health_emp, "is_employer_only": False}

		# 5. Health Insurance Employer (statistical)
		health_empr = gross * (flt(self.settings.health_employer_rate) / 100)
		results["Health Insurance Employer BI"] = {"amount": health_empr, "is_employer_only": True}

		# 6. Training Fund Employee
		training_emp = gross * (flt(self.settings.training_employee_rate) / 100)
		results["Training Fund Employee BI"] = {"amount": training_emp, "is_employer_only": False}

		# 7. Training Fund Employer (statistical)
		training_empr = gross * (flt(self.settings.training_employer_rate) / 100)
		results["Training Fund Employer BI"] = {"amount": training_empr, "is_employer_only": True}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results
