"""Seychelles statutory deduction calculator.

Reference: Seychelles Revenue Commission (SRC), citizen rates from 1 June 2018
- PAYE: Progressive 0-30%; reads from settings.paye_bands (monthly) if populated
  Monthly bands:
  0 - 8,555.50 SCR       : 0%
  8,555.50 - 10,000      : 15%
  10,000 - 83,333        : 20%
  Over 83,333            : 30%
- Social Security (SSCR): Employer 5% (capped)
- No employee social security contribution
- Tax-free threshold: SCR 8,555.50/month (read from settings.tax_free_threshold)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

_HARDCODED_PAYE_BRACKETS = [
    (8555.50, 10000, 0.15),
    (10000, 83333, 0.20),
    (83333, 0, 0.30),
]
_DEFAULT_TAX_FREE_THRESHOLD = 8555.50


class SeychellesCalculator(BaseCalculator):
    """Seychelles statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. Social Security - Employer only (5%, capped)
        ss_rate_val = getattr(self.settings, 'social_security_rate', None)
        ss_rate = flt(ss_rate_val if ss_rate_val is not None else 5) / 100
        ss_ceiling_val = getattr(self.settings, 'social_security_ceiling', None)
        ss_ceiling = flt(ss_ceiling_val if ss_ceiling_val is not None else 15000)
        ss_base = min(gross, ss_ceiling) if gross > 0 else 0
        ss_empr = ss_base * ss_rate
        results["Social Security Employer"] = {
            "amount": ss_empr, "is_employer_only": True,
        }

        # 2. PAYE - progressive
        paye = self._compute_paye(gross)
        if paye > 0:
            results["PAYE"] = {
                "amount": paye, "is_employer_only": False,
            }

        return results

    def _compute_paye(self, gross):
        """PAYE progressive monthly bands.

        Reads from settings.paye_bands (monthly amounts) if populated; otherwise
        falls back to the SRC monthly bands above, with the tax-free threshold read
        from settings.tax_free_threshold (default 8,555.50 SCR/month).
        """
        if gross <= 0:
            return 0

        bands = getattr(self.settings, 'paye_bands', None)
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if gross <= lower:
                    break
                top = upper if upper > 0 else gross
                amount = min(gross, top) - lower
                if amount > 0:
                    tax += amount * rate
            return tax

        # Hardcoded monthly-band fallback
        tfr_val = getattr(self.settings, 'tax_free_threshold', None)
        threshold = flt(tfr_val if tfr_val is not None else _DEFAULT_TAX_FREE_THRESHOLD)
        if gross <= threshold:
            return 0
        tax = 0
        for lower, upper, rate in _HARDCODED_PAYE_BRACKETS:
            if gross <= lower:
                break
            top = upper if upper > 0 else gross
            amount = min(gross, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax
