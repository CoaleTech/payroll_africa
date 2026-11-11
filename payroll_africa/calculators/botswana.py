"""Botswana statutory deduction calculator.

Reference: Botswana Unified Revenue Service (BURS)
- PAYE only (no mandatory national social security)
- Progressive PAYE: 0% - 25% (2025/2026 tax year)
- Tax year: 1 July - 30 June
- Employers may optionally contribute to private pension/provident funds
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class BotswanaCalculator(BaseCalculator):
    """Botswana statutory deduction calculator (2025/2026 rates).

    Botswana has no mandatory national social security scheme.
    Only PAYE is statutorily required.
    """

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # PAYE - progressive tax on gross income
        paye = self._compute_paye(gross)
        results["PAYE"] = {
            "amount": paye,
            "is_employer_only": False,
        }

        return results

    def _compute_paye(self, gross_monthly):
        """Compute PAYE using progressive annual bands (2025/2026).

        Annual chargeable income bands (BWP):
        0 - 48,000       : 0%
        48,001 - 84,000  : 5%
        84,001 - 120,000 : 12.5%
        120,001 - 156,000: 18.75%
        Over 156,000     : 25%
        """
        if gross_monthly <= 0:
            return 0

        annual_income = gross_monthly * 12
        tax_free_threshold = self._num("tax_free_threshold", 48000)

        if annual_income <= tax_free_threshold:
            return 0

        tax = 0
        bands = self.settings.paye_bands or []

        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100

                if annual_income <= lower:
                    break

                band_top = upper if upper > 0 else annual_income
                taxable_in_band = min(annual_income, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            # Fallback hardcoded 2025/2026 bands
            tax = self._paye_hardcoded(annual_income, tax_free_threshold)

        # Convert annual tax to monthly
        monthly_tax = tax / 12
        return monthly_tax

    def _paye_hardcoded(self, annual_income, threshold):
        """Hardcoded 2025/2026 BURS PAYE bands.

        Applied to taxable = annual_income - threshold (BWP 48,000), so each
        bracket is 36,000 wide above the threshold.
        """
        taxable = annual_income - threshold
        if taxable <= 0:
            return 0

        tax = 0
        brackets = [
            (0, 36000, 0.05),        # 48,001 - 84,000
            (36000, 72000, 0.125),   # 84,001 - 120,000
            (72000, 108000, 0.1875), # 120,001 - 156,000
            (108000, 0, 0.25),       # Over 156,000
        ]

        for lower, upper, rate in brackets:
            if taxable <= lower:
                break
            top = upper if upper > 0 else taxable
            amount = min(taxable, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
