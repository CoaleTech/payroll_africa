"""Eswatini statutory deduction calculator.

Reference: Eswatini Revenue Service (ERS), ENPF
- PAYE: Progressive 0-33% (annual bands)
  0 - 100,000 SZL    : 0 + 20% over 0
  100,001 - 150,000  : 20,000 + 25% over 100,000
  150,001 - 200,000  : 32,500 + 30% over 150,000
  Over 200,000       : 47,500 + 33% over 200,000
- ENPF: Employee 5%, Employer 5% (capped)
  Cap increases annually:
  2025: E400/month total (E200 each)
  2026: E430/month total (E215 each)
  2027: E460/month total (E230 each)
- Tax rebate: E8,200/year (E683.33/month)
  Secondary rebate (age 60+): E2,700/year
- Skills Development Levy: Employer 1%
- Tax year: July 1 - June 30
- ENPF is deductible before PAYE calculation
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class EswatiniCalculator(BaseCalculator):
    """Eswatini statutory deduction calculator (2025/2026 tax year)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. ENPF Employee (5%, capped)
        enpf_emp = self._compute_enpf(gross)
        results["ENPF Employee"] = {
            "amount": enpf_emp, "is_employer_only": False,
        }

        # ENPF Employer (5%, capped)
        enpf_empr = self._compute_enpf(gross)
        results["ENPF Employer"] = {
            "amount": enpf_empr, "is_employer_only": True,
        }

        # 2. Skills Development Levy - Employer only (1%)
        sdl = gross * (flt(self.settings.sdl_rate or 1) / 100) if gross > 0 else 0
        results["Skills Development Levy"] = {
            "amount": sdl, "is_employer_only": True,
        }

        # 3. PAYE - progressive (after ENPF deduction)
        taxable = max(gross - enpf_emp, 0)
        paye = self._compute_paye(taxable)
        if paye > 0:
            results["PAYE"] = {
                "amount": paye, "is_employer_only": False,
            }

        return results

    def _compute_enpf(self, gross):
        """ENPF: 5% of gross, capped at monthly limit."""
        rate = flt(self.settings.enpf_rate or 5) / 100
        # Default cap: E400/month total = E200/month per side (2025)
        cap_total = flt(self.settings.enpf_cap_total or 400)
        cap_per_side = cap_total / 2
        contribution = gross * rate
        return min(contribution, cap_per_side) if gross > 0 else 0

    def _compute_paye(self, taxable_income):
        """Compute PAYE using annual progressive bands.

        Annual taxable income bands (SZL):
        0 - 100,000      : 0 + 20% over 0
        100,001 - 150,000: 20,000 + 25% over 100,000
        150,001 - 200,000: 32,500 + 30% over 150,000
        Over 200,000     : 47,500 + 33% over 200,000
        """
        if taxable_income <= 0:
            return 0

        annual = taxable_income * 12

        # Apply tax rebate
        rebate = flt(self.settings.tax_rebate_annual or 8200)

        if annual <= 100000:
            tax = annual * 0.20
        elif annual <= 150000:
            tax = 20000 + (annual - 100000) * 0.25
        elif annual <= 200000:
            tax = 32500 + (annual - 150000) * 0.30
        else:
            tax = 47500 + (annual - 200000) * 0.33

        tax = max(tax - rebate, 0)
        return tax / 12
