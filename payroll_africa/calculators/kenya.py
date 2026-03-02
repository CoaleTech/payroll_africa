from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class KenyaCalculator(BaseCalculator):
	"""Kenya statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. NSSF (deducted before PAYE - exempted_from_income_tax=1)
		nssf = self._compute_nssf(gross)
		results["NSSF Employee"] = {"amount": nssf["employee"], "is_employer_only": False}
		results["NSSF Employer"] = {"amount": nssf["employer"], "is_employer_only": True}

		# 2. SHIF (deducted before PAYE)
		shif_rate = flt(self.settings.shif_rate) / 100
		shif_min = flt(self.settings.shif_minimum)
		shif = max(gross * shif_rate, shif_min) if gross > 0 else 0
		results["SHIF"] = {"amount": shif, "is_employer_only": False}

		# 3. Housing Levy (deducted before PAYE per 2025 rules)
		emp_ahl = gross * (flt(self.settings.ahl_employee_rate) / 100)
		empr_ahl = gross * (flt(self.settings.ahl_employer_rate) / 100)
		results["Housing Levy"] = {"amount": emp_ahl, "is_employer_only": False}
		results["Employer Housing Levy"] = {"amount": empr_ahl, "is_employer_only": True}

		# 4. NITA (employer only, flat amount)
		results["NITA"] = {"amount": flt(self.settings.nita_amount), "is_employer_only": True}

		# PAYE is NOT computed here - HRMS handles it via Income Tax Slab
		return results

	def _compute_nssf(self, gross):
		"""Compute NSSF Tier I + Tier II per 2025 Act."""
		s = self.settings

		# Tier I: rate% of gross, capped
		tier1_rate = flt(s.nssf_tier1_rate) / 100
		tier1_cap = flt(s.nssf_tier1_cap)
		tier1_emp = min(gross * tier1_rate, tier1_cap)
		tier1_empr = tier1_emp  # employer matches

		# Tier II: rate% of (gross - lower_limit), capped
		tier1_upper = flt(s.nssf_tier1_upper_limit)
		tier2_rate = flt(s.nssf_tier2_rate) / 100
		tier2_cap = flt(s.nssf_tier2_cap)
		tier2_base = max(gross - tier1_upper, 0)
		tier2_emp = min(tier2_base * tier2_rate, tier2_cap)
		tier2_empr = tier2_emp

		return {
			"employee": tier1_emp + tier2_emp,
			"employer": tier1_empr + tier2_empr,
		}
