"""Gabon statutory deduction calculator.

Reference: CNSS Gabon (as of Dec 2025 reform, effective Jan 2026)
  New total rate: 23% (was 19%)
- CNSS Pension (Vieillesse): Employee 5%, Employer 11% (16% total)
- CNSS Family Allowances: Employer 5%
- CNSS Work Injury: Employer 2%
- CNSS Health (CNAMGS): Employer 4.1%
  Total employer: 22.1% + Employee 5% = ~27.1% (before the reform)
  Post-reform 2026: Total 23% (to be configured via settings)

Ceiling: XAF 1,500,000/month (2026)
PIT (IR): Progressive 0-35%
  0 - 2,160,000/year (180,000/month): 0%
  2,160,001 - 3,000,000: 5%
  3,000,001 - 4,800,000: 10%
  4,800,001 - 7,200,000: 15%
  7,200,001 - 9,600,000: 20%
  9,600,001 - 12,000,000: 25%
  12,000,001 - 24,000,000: 30%
  Over 24,000,000: 35%
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class GabonCalculator(BaseCalculator):
    """Gabon statutory deduction calculator (2026 rates, post-reform)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # Use 2026 post-reform rates by default, but allow override via settings
        use_2026_reform = self.settings.get("use_2026_reform", 1)

        if use_2026_reform:
            # Post-reform 2026: separate rates (cnss_total_rate is not a DocType field)
            employee_share = self._num("cnss_employee_rate", 5) / 100
            employer_share = self._num("cnss_employer_rate", 18) / 100
        else:
            # Pre-reform: separate rates
            employee_share = self._num("cnss_employee_rate", 2.5) / 100
            employer_share = self._num("cnss_employer_rate", 16) / 100

        ceiling = flt(self.settings.cnss_ceiling or 1500000)
        base = min(gross, ceiling) if gross > 0 else 0

        # 1. CNSS Employee
        cnss_emp = base * employee_share
        results["CNSS Employee"] = {
            "amount": cnss_emp,
            "is_employer_only": False,
        }

        # 2. CNSS Employer
        cnss_empr = base * employer_share
        results["CNSS Employer"] = {
            "amount": cnss_empr,
            "is_employer_only": True,
        }

        # 3. PIT (IR) - progressive
        taxable = max(gross - cnss_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit,
                "is_employer_only": False,
            }

        return results

    def _compute_pit(self, taxable_income):
        """Compute PIT using progressive annual bands.

        Annual taxable income bands (XAF):
        0 - 2,160,000      : 0%
        2,160,001 - 3,000,000 : 5%
        3,000,001 - 4,800,000 : 10%
        4,800,001 - 7,200,000 : 15%
        7,200,001 - 9,600,000 : 20%
        9,600,001 - 12,000,000: 25%
        12,000,001 - 24,000,000: 30%
        Over 24,000,000      : 35%
        """
        if taxable_income <= 0:
            return 0

        annual_income = taxable_income * 12
        threshold = self._num("pit_threshold_annual", 2160000)

        if annual_income <= threshold:
            return 0

        bands = getattr(self.settings, "pit_bands", None) or []
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if annual_income <= lower:
                    break
                band_top = upper if upper > 0 else annual_income
                amount = min(annual_income, band_top) - lower
                if amount > 0:
                    tax += amount * rate
            return tax / 12

        # Hardcoded fallback (annual XAF)
        tax = 0
        brackets = [
            (2160000, 3000000, 0.05),
            (3000000, 4800000, 0.10),
            (4800000, 7200000, 0.15),
            (7200000, 9600000, 0.20),
            (9600000, 12000000, 0.25),
            (12000000, 24000000, 0.30),
            (24000000, 0, 0.35),
        ]
        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
