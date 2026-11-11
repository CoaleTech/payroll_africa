"""Djibouti statutory deduction calculator.

Reference: ISSA / PwC WWTS 2024 (limited public data).
CNSS health branch rates: employee ~2%, employer ~5% (estimates).
PIT: progressive annual brackets, divided by 12.
"""
from frappe.utils import flt

from payroll_africa.calculators.base import BaseCalculator


class DjiboutiCalculator(BaseCalculator):
	"""Djibouti statutory deduction calculator."""

	def compute(self, salary_slip):
		gross = self.get_gross_pay(salary_slip)
		results = {}

		# CNSS ceiling: None = not configured (use default 400,000).
		# 0 is valid (uncapped). Use 'is not None' not 'or' so 0 passes through.
		ceiling_raw = getattr(self.settings, "cnss_ceiling", None)
		ceiling = flt(ceiling_raw) if ceiling_raw is not None else 400000
		base = min(gross, ceiling) if (gross > 0 and ceiling > 0) else (gross if gross > 0 else 0)

		emp_rate_raw = getattr(self.settings, "cnss_employee_rate", None)
		emp_rate = flt(emp_rate_raw) if emp_rate_raw is not None else 2
		empr_rate_raw = getattr(self.settings, "cnss_employer_rate", None)
		empr_rate = flt(empr_rate_raw) if empr_rate_raw is not None else 5

		cnss_emp = base * (emp_rate / 100)
		cnss_empr = base * (empr_rate / 100)
		results["CNSS Employee"] = {"amount": cnss_emp, "is_employer_only": False}
		results["CNSS Employer"] = {"amount": cnss_empr, "is_employer_only": True}

		taxable = max(gross - cnss_emp, 0)
		pit = self._compute_pit(taxable)
		# Always write PIT so the engine overwrites the HRMS slab value even when 0.
		if pit > 0:
			results["PIT"] = {"amount": pit, "is_employer_only": False}
		return results

	def _compute_pit(self, taxable_income):
		"""Compute monthly PIT from annual progressive brackets.

		Reads pit_bands from settings when configured (annual DJF);
		falls back to hardcoded ISSA/PwC estimates.
		pit_threshold sets the annual tax-free floor when using the fallback.
		"""
		if taxable_income <= 0:
			return 0
		annual = taxable_income * 12

		bands = getattr(self.settings, "pit_bands", None) or []
		threshold_raw = getattr(self.settings, "pit_threshold", None)
		threshold = flt(threshold_raw) if threshold_raw is not None else 240000

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

		# Hardcoded fallback (annual DJF brackets)
		if annual <= threshold:
			return 0
		tax = 0
		for lower, upper, rate in [
			(240000, 600000, 0.10),
			(600000, 1200000, 0.20),
			(1200000, 0, 0.30),
		]:
			if annual <= lower:
				break
			amount = min(annual, upper if upper > 0 else annual) - lower
			if amount > 0:
				tax += amount * rate
		return tax / 12
