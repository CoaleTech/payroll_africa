from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class UgandaCalculator(BaseCalculator):
	"""Uganda statutory deduction calculator (2025 rates)."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# 1. NSSF Employee (pre-PAYE, exempted_from_income_tax=1)
		nssf_emp = gross * (flt(self.settings.nssf_employee_rate) / 100)
		results["NSSF Employee UG"] = {"amount": nssf_emp, "is_employer_only": False}

		# 2. LST - graduated based on monthly gross income
		lst_annual = self._compute_lst(gross)
		lst_monthly = flt(lst_annual / 12, 2)
		results["LST"] = {"amount": lst_monthly, "is_employer_only": False}

		# 3. PAYE - computed using monthly progressive bands
		paye = self._compute_paye(gross, nssf_emp)
		results["PAYE UG"] = {"amount": paye, "is_employer_only": False}

		return results

	def _compute_lst(self, monthly_gross):
		"""Compute annual LST based on graduated income bands from settings.

		LST bands use the Uganda PAYE Band table where:
		- from_amount / to_amount = monthly income range
		- rate = annual LST amount (not a percentage)
		Bands are checked highest-first; first match wins.
		"""
		bands = self.settings.lst_bands or []
		# Sort descending by from_amount so highest bracket matches first
		sorted_bands = sorted(bands, key=lambda b: flt(b.from_amount), reverse=True)
		for band in sorted_bands:
			if monthly_gross >= flt(band.from_amount):
				return flt(band.rate)
		return 0

	def _compute_paye(self, gross, nssf_employee):
		"""Compute PAYE using monthly progressive bands.

		Uganda PAYE: NSSF employee contribution is deducted before tax.
		No personal relief in Uganda — the first band (0-235,000) is at 0%.
		"""
		taxable = gross - nssf_employee
		if taxable <= 0:
			return 0

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

		return flt(tax, 2)
