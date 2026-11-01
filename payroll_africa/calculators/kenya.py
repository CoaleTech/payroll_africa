from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class KenyaCalculator(BaseCalculator):
	"""Kenya statutory deduction calculator (2025/2026 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. NSSF Employee (exempted_from_income_tax=1, deducted before PAYE)
		nssf = self._compute_nssf(gross)
		results["NSSF Employee"] = {"amount": nssf["employee"], "is_employer_only": False}

		# 2. SHIF (exempted_from_income_tax=1)
		shif_rate = flt(self.settings.shif_rate) / 100
		shif_min = flt(self.settings.shif_minimum)
		shif = max(gross * shif_rate, shif_min) if gross > 0 else 0
		results["SHIF"] = {"amount": shif, "is_employer_only": False}

		# 3. Housing Levy employee portion (exempted_from_income_tax=1 per 2025 rules)
		emp_ahl = gross * (flt(self.settings.ahl_employee_rate) / 100)
		results["Housing Levy"] = {"amount": emp_ahl, "is_employer_only": False}

		# 4. PAYE — computed using monthly paye_bands + personal relief credit.
		#    The engine overwrites the HRMS Income Tax Slab value with this result.
		allowable = nssf["employee"] + shif + emp_ahl
		paye = self._compute_paye(gross, allowable)
		results["PAYE"] = {"amount": paye, "is_employer_only": False}

		# Employer-only components
		results["NSSF Employer"] = {"amount": nssf["employer"], "is_employer_only": True}

		empr_ahl = gross * (flt(self.settings.ahl_employer_rate) / 100)
		results["Employer Housing Levy"] = {"amount": empr_ahl, "is_employer_only": True}

		nita = flt(self.settings.nita_amount)
		if nita > 0:
			results["NITA"] = {"amount": nita, "is_employer_only": True}

		return results

	def _compute_paye(self, gross, allowable_deductions):
		"""Compute PAYE using monthly progressive bands with personal relief credit.

		Kenya PAYE: personal relief is a tax credit (subtracted from computed tax,
		floored at 0). Monthly bands are read from settings.paye_bands.

		Band boundaries store from_amount = previous to_amount + 1 (e.g. 24001).
		We adjust the floor to max(from_amount - 1, 0) so income exactly at a
		boundary is taxed correctly and no shilling of width is lost.
		"""
		taxable = gross - allowable_deductions
		if taxable <= 0:
			return 0

		tax = 0
		bands = self.settings.paye_bands or []
		for band in bands:
			lower = flt(band.from_amount)
			upper = flt(band.to_amount)
			rate = flt(band.rate) / 100

			if taxable < lower:
				break

			floor = max(lower - 1, 0)
			band_ceiling = upper if upper > 0 else taxable
			taxable_in_band = min(taxable, band_ceiling) - floor
			if taxable_in_band > 0:
				tax += taxable_in_band * rate

		personal_relief = flt(self.settings.personal_relief)
		paye = max(tax - personal_relief, 0)

		return round(flt(paye), 2)

	def _compute_nssf(self, gross):
		"""Compute NSSF Tier I + Tier II per NSSF Act 2013 (Year 4, Feb 2026 rates).

		Tier I:  rate% of gross up to nssf_tier1_upper_limit (LEL), capped at
		         nssf_tier1_cap.
		Tier II: rate% of gross above LEL, capped at nssf_tier2_cap.
		         NOTE: nssf_tier2_cap is a *contribution* cap, not the Upper
		         Earnings Limit; the field label "Upper Earnings Limit" is incorrect.
		Employer contribution mirrors employee in both tiers.
		"""
		s = self.settings

		tier1_rate = flt(s.nssf_tier1_rate) / 100
		tier2_rate = flt(s.nssf_tier2_rate) / 100
		lel = flt(s.nssf_tier1_upper_limit)   # Lower Earnings Limit
		tier1_cap = flt(s.nssf_tier1_cap)      # Max Tier I contribution
		tier2_cap = flt(s.nssf_tier2_cap)      # Max Tier II contribution

		# Tier I: rate of earnings up to LEL, subject to cap
		tier1_base = min(gross, lel) if gross > 0 else 0
		tier1 = min(tier1_base * tier1_rate, tier1_cap) if tier1_cap else tier1_base * tier1_rate

		# Tier II: rate of earnings above LEL, subject to contribution cap
		tier2_base = max(gross - lel, 0) if gross > 0 else 0
		tier2 = min(tier2_base * tier2_rate, tier2_cap) if tier2_cap else tier2_base * tier2_rate

		total = tier1 + tier2
		return {"employee": total, "employer": total}
