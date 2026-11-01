from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class DRCCalculator(BaseCalculator):
	"""DRC statutory deduction calculator (2025 rates)."""

	def _rate(self, field, default):
		value = getattr(self.settings, field, None)
		return default if value is None else flt(value)

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. INSS Pension Employee (exempted_from_income_tax=1 → reduces IPR taxable)
		inss_emp = gross * self._rate("inss_pension_employee_rate", 5) / 100
		results["INSS Pension Employee CD"] = {"amount": inss_emp, "is_employer_only": False}

		# 2. INSS Pension Employer
		inss_empr = gross * self._rate("inss_pension_employer_rate", 5) / 100
		results["INSS Pension Employer CD"] = {"amount": inss_empr, "is_employer_only": True}

		# 3. INSS Occupational Risks (employer only)
		occ_risk = gross * self._rate("inss_occupational_risks_rate", 1.5) / 100
		results["INSS Occupational Risks CD"] = {"amount": occ_risk, "is_employer_only": True}

		# 4. INSS Family Benefits (employer only)
		family = gross * self._rate("inss_family_benefits_rate", 6.5) / 100
		results["INSS Family Benefits CD"] = {"amount": family, "is_employer_only": True}

		# 5. INPP (employer only)
		inpp = gross * self._rate("inpp_rate", 3) / 100
		results["INPP CD"] = {"amount": inpp, "is_employer_only": True}

		# 6. ONEM (employer only)
		onem = gross * self._rate("onem_rate", 0.2) / 100
		results["ONEM CD"] = {"amount": onem, "is_employer_only": True}

		# 7. IPR/PAYE (employee only) — computed from monthly paye_bands
		taxable = max(gross - inss_emp, 0)
		ipr = self._compute_ipr(taxable)
		if ipr > 0:
			results["PAYE CD"] = {"amount": ipr, "is_employer_only": False}

		return results

	def _compute_ipr(self, taxable):
		"""Compute monthly IPR/PAYE from paye_bands (monthly CDF amounts).

		Reads paye_bands from settings if populated; falls back to hardcoded:
		  0 - 162,000     : 3%
		  162,001 - 1,800,000: 15%
		  1,800,001 - 3,600,000: 30%
		  Over 3,600,000  : 40%
		"""
		if taxable <= 0:
			return 0

		bands = getattr(self.settings, "paye_bands", None) or []
		if bands:
			tax = 0
			for band in bands:
				lower = flt(band.from_amount)
				upper = flt(band.to_amount)
				rate = flt(band.rate) / 100
				if taxable <= lower:
					break
				band_top = upper if upper > 0 else taxable
				amount = min(taxable, band_top) - lower
				if amount > 0:
					tax += amount * rate
			return tax

		# Hardcoded fallback (monthly CDF)
		tax = 0
		for lower, upper, rate in [
			(0, 162000, 0.03),
			(162001, 1800000, 0.15),
			(1800001, 3600000, 0.30),
			(3600001, 0, 0.40),
		]:
			if taxable <= lower:
				break
			top = upper if upper > 0 else taxable
			amount = min(taxable, top) - lower
			if amount > 0:
				tax += amount * rate
		return tax
