"""Eritrea statutory deduction calculator.

Reference: National Insurance Corporation of Eritrea (NICE) — very limited data.
Rates are estimates from ISSA sources: employee ~6%, employer ~6%.
PIT: monthly progressive bands (best available 2024-25).
"""
from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class EritreaCalculator(BaseCalculator):
	"""Eritrea statutory deduction calculator."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# NICE rates: None = not configured (use default). 0 is valid.
		emp_rate_raw = getattr(self.settings, "nice_employee_rate", None)
		emp_rate = flt(emp_rate_raw) if emp_rate_raw is not None else 6
		empr_rate_raw = getattr(self.settings, "nice_employer_rate", None)
		empr_rate = flt(empr_rate_raw) if empr_rate_raw is not None else 6

		nice_emp = gross * (emp_rate / 100) if gross > 0 else 0
		nice_empr = gross * (empr_rate / 100) if gross > 0 else 0
		results["NICE Employee"] = {"amount": nice_emp, "is_employer_only": False}
		results["NICE Employer"] = {"amount": nice_empr, "is_employer_only": True}

		taxable = max(gross - nice_emp, 0)
		pit = self._compute_pit(taxable)
		# Always write PIT so the engine overwrites the HRMS slab value even when 0.
		if pit > 0:
			results["PIT"] = {"amount": pit, "is_employer_only": False}
		return results

	def _compute_pit(self, taxable_income):
		"""Compute monthly PIT from progressive bands.

		Reads pit_bands from settings when configured (monthly ERN);
		falls back to hardcoded monthly bands. tax_free_threshold sets
		the monthly floor when using the fallback.
		"""
		if taxable_income <= 0:
			return 0

		bands = getattr(self.settings, "pit_bands", None) or []
		threshold_raw = getattr(self.settings, "tax_free_threshold", None)
		threshold = flt(threshold_raw) if threshold_raw is not None else 800

		if bands:
			tax = 0
			for band in bands:
				lower = flt(band.from_amount)
				upper = flt(band.to_amount)
				rate = flt(band.rate) / 100
				if taxable_income < lower:
					break
				floor = max(lower - 1, 0)
				band_top = upper if upper > 0 else taxable_income
				amount = min(taxable_income, band_top) - floor
				if amount > 0:
					tax += amount * rate
			return tax

		# Hardcoded fallback (monthly ERN bands)
		if taxable_income <= threshold:
			return 0
		tax = 0
		for lower, upper, rate in [
			(800, 1000, 0.05),
			(1000, 1500, 0.10),
			(1500, 2000, 0.15),
			(2000, 3000, 0.20),
			(3000, 0, 0.30),
		]:
			if taxable_income <= lower:
				break
			amount = min(taxable_income, upper if upper > 0 else taxable_income) - lower
			if amount > 0:
				tax += amount * rate
		return tax
