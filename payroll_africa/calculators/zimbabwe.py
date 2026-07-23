"""Zimbabwe statutory deduction calculator.

Reference: ZIMRA (Zimbabwe Revenue Authority)
- PAYE: Progressive 0%/20%/25%/30%/35%/40% with formula method
  Monthly formula: (gross x rate) - deduction
- Tax-free threshold: ZiG 2,800/month or USD 100/month
- AIDS Levy: 3% on tax payable (not on gross)
- NSSA Pension: Employee 4.5%, Employer 4.5% (capped)
- Tax credits: Medical, disabled, blind, elderly (55+)
- Dual currency: ZiG/USD (separate tax tables)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class ZimbabweCalculator(BaseCalculator):
    """Zimbabwe statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. NSSA Pension - Employee (4.5%, capped)
        nssa_employee = self._compute_nssa(gross)
        results["NSSA Pension Employee"] = {
            "amount": nssa_employee,
            "is_employer_only": False,
        }

        # NSSA Pension - Employer (4.5%, capped)
        results["NSSA Pension Employer"] = {
            "amount": nssa_employee,  # Same amount
            "is_employer_only": True,
        }

        # 2. PAYE - progressive (after NSSA deduction)
        taxable_income = max(gross - nssa_employee, 0)
        paye = self._compute_paye(taxable_income)

        # 3. AIDS Levy - 3% of tax payable
        aids_levy = paye * (flt(self.settings.aids_levy_rate or 3) / 100)

        if paye > 0:
            results["PAYE"] = {
                "amount": paye,
                "is_employer_only": False,
            }
        if aids_levy > 0:
            results["AIDS Levy"] = {
                "amount": aids_levy,
                "is_employer_only": False,
            }

        return results

    def _compute_nssa(self, gross):
        """NSSA pension: 4.5% of gross, capped.
        Ceiling: ZiG 1,914,360/year = ZiG 159,530/month (as of 2025)
        """
        ceiling_annual = flt(self.settings.nssa_annual_ceiling or 8400)   # USD 700/mo x 12 (NSSA 2025)
        ceiling_monthly = ceiling_annual / 12
        rate = flt(self.settings.nssa_rate or 4.5) / 100
        base = min(gross, ceiling_monthly) if gross > 0 else 0
        return base * rate

    def _compute_paye(self, taxable_income):
        """Compute PAYE using formula method (monthly tables).

        Monthly formula method (USD tables 2025):
        0 - 100       : 0%    - 0
        100.01 - 300  : 20%   - 20
        300.01 - 1000 : 25%   - 35
        1000.01 - 2000: 30%   - 85
        2000.01 - 3000: 35%   - 185
        3000.01+      : 40%   - 335
        """
        if taxable_income <= 0:
            return 0

        currency = self.settings.get("currency_mode", "USD")
        threshold = flt(self.settings.tax_free_threshold or 100)

        if taxable_income <= threshold:
            return 0

        # Apply formula method
        bands = self.settings.paye_bands or []
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                deduction = flt(band.deduction or 0)
                if taxable_income <= lower:
                    break
                band_top = upper if upper > 0 else taxable_income
                if taxable_income <= band_top:
                    tax = taxable_income * rate - deduction
                    break
            return max(tax, 0)
        else:
            return self._paye_hardcoded(taxable_income)

    def _paye_hardcoded(self, taxable_income):
        """Hardcoded formula method (USD monthly)."""
        if taxable_income <= 100:
            return 0
        elif taxable_income <= 300:
            return max(taxable_income * 0.20 - 20, 0)
        elif taxable_income <= 1000:
            return max(taxable_income * 0.25 - 35, 0)
        elif taxable_income <= 2000:
            return max(taxable_income * 0.30 - 85, 0)
        elif taxable_income <= 3000:
            return max(taxable_income * 0.35 - 185, 0)
        else:
            return max(taxable_income * 0.40 - 335, 0)
