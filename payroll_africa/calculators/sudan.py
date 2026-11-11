"""Sudan statutory deduction calculator.

Reference: National Social Insurance Fund (NSIF) — conflict-affected, limited data.
Estimates: employee ~8%, employer ~17% on gross up to ceiling.
PIT: progressive annual brackets, divided by 12.
Note: Data reliability is low due to conflict situation. All rates are estimates.
"""
from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class SudanCalculator(BaseCalculator):
	"""Sudan statutory deduction calculator."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# NSIF ceiling: None = not configured (use default 100,000). 0 is valid.
		ceiling_raw = getattr(self.settings, "nsif_ceiling", None)
		ceiling = flt(ceiling_raw) if ceiling_raw is not None else 100000
		base = min(gross, ceiling) if (gross > 0 and ceiling > 0) else (gross if gross > 0 else 0)

		emp_rate_raw = getattr(self.settings, "nsif_employee_rate", None)
		emp_rate = flt(emp_rate_raw) if emp_rate_raw is not None else 8
		empr_rate_raw = getattr(self.settings, "nsif_employer_rate", None)
		empr_rate = flt(empr_rate_raw) if empr_rate_raw is not None else 17

		nsif_emp = base * (emp_rate / 100)
		nsif_empr = base * (empr_rate / 100)
		results["NSIF Employee"] = {"amount": nsif_emp, "is_employer_only": False}
		results["NSIF Employer"] = {"amount": nsif_empr, "is_employer_only": True}

		taxable = max(gross - nsif_emp, 0)
		pit = self._compute_pit(taxable)
		# Always write PIT so the engine overwrites the HRMS slab value even when 0.
		if pit > 0:
			results["PIT"] = {"amount": pit, "is_employer_only": False}
		return results

	def _compute_pit(self, taxable_income):
		"""Compute monthly PIT from annual progressive brackets.

		Reads pit_bands from settings when configured (annual SDG);
		falls back to hardcoded annual brackets. tax_free_threshold sets
		the annual floor when using the fallback.
		"""
		if taxable_income <= 0:
			return 0
		annual = taxable_income * 12

		bands = getattr(self.settings, "pit_bands", None) or []
		threshold_raw = getattr(self.settings, "tax_free_threshold", None)
		threshold = flt(threshold_raw) if threshold_raw is not None else 120000

		if bands:
			tax = 0
			for band in bands:
				lower = flt(band.from_amount)
				upper = flt(band.to_amount)
				rate = flt(band.rate) / 100
				if annual < lower:
					break
				floor = max(lower - 1, 0)
				band_top = upper if upper > 0 else annual
				amount = min(annual, band_top) - floor
				if amount > 0:
					tax += amount * rate
			return tax / 12

		# Hardcoded fallback (annual SDG brackets)
		if annual <= threshold:
			return 0
		tax = 0
		for lower, upper, rate in [
			(120000, 360000, 0.10),
			(360000, 720000, 0.15),
			(720000, 0, 0.20),
		]:
			if annual <= lower:
				break
			amount = min(annual, upper if upper > 0 else annual) - lower
			if amount > 0:
				tax += amount * rate
		return tax / 12
