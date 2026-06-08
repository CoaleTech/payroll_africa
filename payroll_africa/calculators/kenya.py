from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class KenyaCalculator(BaseCalculator):
	"""Kenya statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. NSSF Employee (deducted before PAYE - exempted_from_income_tax=1)
		nssf = self._compute_nssf(gross)
		results["NSSF Employee"] = {"amount": nssf["employee"], "is_employer_only": False}

		# 2. SHIF (deducted before PAYE)
		shif_rate = flt(self.settings.shif_rate) / 100
		shif_min = flt(self.settings.shif_minimum)
		shif = max(gross * shif_rate, shif_min) if gross > 0 else 0
		results["SHIF"] = {"amount": shif, "is_employer_only": False}

		# 3. Housing Levy - employee portion only (deducted before PAYE per 2025 rules)
		emp_ahl = gross * (flt(self.settings.ahl_employee_rate) / 100)
		results["Housing Levy"] = {"amount": emp_ahl, "is_employer_only": False}

		# Note: PAYE is NOT computed here — it is handled by HRMS via Income Tax Slab.
		# The NSSF, SHIF, and Housing Levy amounts above are deducted before PAYE
		# by configuring them as pre-tax deductions in the Salary Structure.

		# Employer-only components
		results["NSSF Employer"] = {"amount": nssf["employer"], "is_employer_only": True}

		empr_ahl = gross * (flt(self.settings.ahl_employer_rate) / 100)
		results["Employer Housing Levy"] = {"amount": empr_ahl, "is_employer_only": True}

		nita = flt(self.settings.nita_amount)
		if nita > 0:
			results["NITA"] = {"amount": nita, "is_employer_only": True}

		return results

	def _compute_paye(self, gross, allowable_deductions):
		"""Compute PAYE using monthly progressive bands.

		Kenya PAYE: personal relief is a TAX CREDIT (subtracted from tax),
		not an income deduction. This matches KRA computation.
		"""
		taxable = gross - allowable_deductions
		if taxable <= 0:
			return 0

		# Monthly progressive bands from Kenya Payroll Settings
		tax = 0
		bands = self.settings.paye_bands or []
		for band in bands:
			lower = flt(band.from_amount)
			upper = flt(band.to_amount)
			rate = flt(band.rate) / 100

			if taxable <= lower:
				break

			band_ceiling = upper if upper > 0 else taxable
			taxable_in_band = min(taxable, band_ceiling) - lower
			if taxable_in_band > 0:
				tax += taxable_in_band * rate

		# Personal relief is a TAX CREDIT (subtracted from computed tax)
		personal_relief = flt(self.settings.personal_relief)
		paye = max(tax - personal_relief, 0)

		return flt(paye, 2)

	def _compute_nssf(self, gross):
		"""Compute NSSF Tier I + Tier II per NSSF Act 2013 (2025 rates).

		Tier I: rate% of gross up to LEL, capped at nssf_tier1_cap.
		Tier II: rate% of gross above LEL, capped at nssf_tier2_cap.
		Employer contribution mirrors employee in both tiers.
		"""
		s = self.settings

		tier1_rate = flt(s.nssf_tier1_rate) / 100
		tier2_rate = flt(s.nssf_tier2_rate) / 100
		lel = flt(s.nssf_tier1_upper_limit)   # Lower Earnings Limit
		tier1_cap = flt(s.nssf_tier1_cap)     # Max Tier I contribution
		tier2_cap = flt(s.nssf_tier2_cap)     # Max Tier II contribution

		# Tier I: rate of earnings up to LEL, subject to cap
		tier1_base = min(gross, lel) if gross > 0 else 0
		tier1 = min(tier1_base * tier1_rate, tier1_cap) if tier1_cap else tier1_base * tier1_rate

		# Tier II: rate of earnings above LEL, subject to cap
		tier2_base = max(gross - lel, 0) if gross > 0 else 0
		tier2 = min(tier2_base * tier2_rate, tier2_cap) if tier2_cap else tier2_base * tier2_rate

		total = tier1 + tier2
		return {
			"employee": total,
			"employer": total,  # employer matches employee
		}
