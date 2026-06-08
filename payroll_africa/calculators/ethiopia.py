"""Ethiopia statutory deduction calculator.

Reference: Income Tax Proclamation No. 286/2002 (as amended by Proclamation 1395/2025)
- Pension: Employee 7%, Employer 11% (capped at ETB 15,000/month)
- PIT: Progressive 0-35% on monthly income (6 brackets, effective July 2025)
- Tax-free threshold: ETB 2,000/month
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class EthiopiaCalculator(BaseCalculator):
    """Ethiopia statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        basic = self.get_basic_pay(salary_slip)
        results = {}

        # 1. Pension contribution (employee share) - 7% of basic, capped
        pension_employee = self._compute_pension_employee(basic)
        results["Pension Employee"] = {
            "amount": pension_employee,
            "is_employer_only": False,
        }

        # Employer pension contribution (11%) - employer-only, not deducted from net
        pension_employer = self._compute_pension_employer(basic)
        results["Pension Employer"] = {
            "amount": pension_employer,
            "is_employer_only": True,
        }

        # 2. PIT (Personal Income Tax) - progressive on gross after pension deduction
        taxable_income = max(gross - pension_employee, 0)
        pit = self._compute_pit(taxable_income)
        results["PIT"] = {
            "amount": pit,
            "is_employer_only": False,
        }

        return results

    def _compute_pension_employee(self, basic):
        """Employee pension: 7% of basic salary, capped at ETB 15,000."""
        ceiling = flt(self.settings.pension_ceiling or 15000)
        base = min(basic, ceiling) if basic > 0 else 0
        return base * (flt(self.settings.pension_employee_rate or 7) / 100)

    def _compute_pension_employer(self, basic):
        """Employer pension: 11% of basic salary, capped at ETB 15,000."""
        ceiling = flt(self.settings.pension_ceiling or 15000)
        base = min(basic, ceiling) if basic > 0 else 0
        return base * (flt(self.settings.pension_employer_rate or 11) / 100)

    def _compute_pit(self, taxable_income):
        """Compute PIT using progressive monthly bands (2025 rates).

        Monthly brackets (ETB):
        0 - 2,000      : 0%
        2,001 - 4,000  : 15%
        4,001 - 7,000  : 20%
        7,001 - 10,000 : 25%
        10,001 - 14,000: 30%
        Over 14,000    : 35%
        """
        if taxable_income <= 0:
            return 0

        tax = 0
        remaining = taxable_income

        bands = self.settings.pit_bands or []
        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100

                if remaining <= lower:
                    break

                band_top = upper if upper > 0 else remaining
                taxable_in_band = min(remaining, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            # Fallback to hardcoded 2025 bands
            tax = self._pit_hardcoded(taxable_income)

        return tax

    def _pit_hardcoded(self, taxable_income):
        """Hardcoded 2025 PIT bands as fallback."""
        tax = 0
        brackets = [
            (2000, 4000, 0.15),
            (4000, 7000, 0.20),
            (7000, 10000, 0.25),
            (10000, 14000, 0.30),
            (14000, 0, 0.35),
        ]

        for lower, upper, rate in brackets:
            if taxable_income <= lower:
                break
            top = upper if upper > 0 else taxable_income
            amount = min(taxable_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
