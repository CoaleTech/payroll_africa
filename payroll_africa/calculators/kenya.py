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

		# 4. PAYE - computed using monthly progressive bands with personal relief as tax credit
		allowable_deductions = nssf["employee"] + shif + emp_ahl
		paye = self._compute_paye(gross, allowable_deductions)
		results["PAYE"] = {"amount": paye, "is_employer_only": False}

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

		Tier I: rate% of pensionable earnings up to Lower Earnings Limit (LEL).
		Tier II: rate% of pensionable earnings between LEL and Upper Earnings Limit (UEL).
		Employer matches employee contribution in both tiers.
		"""
		s = self.settings

		tier1_rate = flt(s.nssf_tier1_rate) / 100
		tier2_rate = flt(s.nssf_tier2_rate) / 100
		lower_limit = flt(s.nssf_tier1_upper_limit)  # LEL (e.g. 8,000)
		upper_limit = flt(s.nssf_tier2_cap)           # UEL (e.g. 72,000)

		# Tier I: rate of pensionable earnings up to LEL
		tier1_pensionable = min(gross, lower_limit)
		tier1_emp = tier1_pensionable * tier1_rate

		# Tier II: rate of pensionable earnings between LEL and UEL
		tier2_pensionable = max(min(gross, upper_limit) - lower_limit, 0)
		tier2_emp = tier2_pensionable * tier2_rate

		return {
			"employee": tier1_emp + tier2_emp,
			"employer": tier1_emp + tier2_emp,
		}
