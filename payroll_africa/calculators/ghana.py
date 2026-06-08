"""Ghana statutory deduction calculator.

Reference: Ghana Revenue Authority (GRA), SSNIT, NPRA
- PAYE: 7-band progressive 0-35% (Act 896, Fourth Schedule)
- SSNIT Tier 1: 13.5% total (employer remits all, includes 2.5% to NHIS)
- SSNIT Tier 2: 5% to licensed trustee
- SSNIT employee visible deduction: 5.5% (deducted before PAYE)
- Employer SSNIT: 13% (pension) + 5% Tier 2 = 18% total employer
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class GhanaCalculator(BaseCalculator):
    """Ghana statutory deduction calculator (2025/2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        basic = self.get_basic_pay(salary_slip)
        results = {}

        # 1. SSNIT Employee contribution - 5.5% of basic salary
        # This is deducted before PAYE calculation
        ssnit_employee = self._compute_ssnit_employee(basic)
        results["SSNIT Employee"] = {
            "amount": ssnit_employee,
            "is_employer_only": False,
        }

        # 2. SSNIT Employer contribution - 13% of basic (Tier 1 pension portion)
        ssnit_employer = self._compute_ssnit_employer(basic)
        results["SSNIT Employer"] = {
            "amount": ssnit_employer,
            "is_employer_only": True,
        }

        # 3. Tier 2 Pension - 5% employer contribution to NPRA-licensed trustee
        tier2_employer = self._compute_tier2_employer(basic)
        results["Tier 2 Pension Employer"] = {
            "amount": tier2_employer,
            "is_employer_only": True,
        }

        # 4. PAYE - progressive on chargeable income (gross - SSNIT employee)
        chargeable_income = max(gross - ssnit_employee, 0)
        paye = self._compute_paye(chargeable_income)
        results["PAYE"] = {
            "amount": paye,
            "is_employer_only": False,
        }

        return results

    def _compute_ssnit_employee(self, basic):
        """Employee SSNIT: 5.5% of basic salary."""
        rate = flt(self.settings.ssnit_employee_rate or 5.5) / 100
        ceiling = flt(self.settings.ssnit_ceiling or 0)  # No ceiling currently
        base = min(basic, ceiling) if ceiling > 0 and basic > 0 else basic
        return base * rate if base > 0 else 0

    def _compute_ssnit_employer(self, basic):
        """Employer SSNIT Tier 1: 13% of basic salary."""
        rate = flt(self.settings.ssnit_employer_rate or 13) / 100
        ceiling = flt(self.settings.ssnit_ceiling or 0)
        base = min(basic, ceiling) if ceiling > 0 and basic > 0 else basic
        return base * rate if base > 0 else 0

    def _compute_tier2_employer(self, basic):
        """Employer Tier 2 Pension: 5% of basic salary."""
        rate = flt(self.settings.tier2_employer_rate or 5) / 100
        ceiling = flt(self.settings.ssnit_ceiling or 0)
        base = min(basic, ceiling) if ceiling > 0 and basic > 0 else basic
        return base * rate if base > 0 else 0

    def _compute_paye(self, chargeable_income_monthly):
        """Compute PAYE using 7-band progressive scale (2025 rates).

        Annual chargeable income bands (GHS):
        0 - 5,880          : 0%
        5,881 - 7,200      : 5%
        7,201 - 8,760      : 10%
        8,761 - 46,760     : 17.5%
        46,761 - 238,760   : 25%
        238,761 - 604,760  : 30%
        Over 604,760       : 35%
        """
        if chargeable_income_monthly <= 0:
            return 0

        annual_chargeable = chargeable_income_monthly * 12
        tax = 0

        bands = self.settings.paye_bands or []
        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100

                if annual_chargeable <= lower:
                    break

                band_top = upper if upper > 0 else annual_chargeable
                taxable_in_band = min(annual_chargeable, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            tax = self._paye_hardcoded(annual_chargeable)

        return tax / 12  # Convert to monthly

    def _paye_hardcoded(self, annual_income):
        """Hardcoded 2025 PAYE annual bands."""
        if annual_income <= 5880:
            return 0

        tax = 0
        brackets = [
            (5880, 7200, 0.05),
            (7200, 8760, 0.10),
            (8760, 46760, 0.175),
            (46760, 238760, 0.25),
            (238760, 604760, 0.30),
            (604760, 0, 0.35),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
