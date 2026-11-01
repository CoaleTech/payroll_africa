"""Libya statutory deduction calculator.

Reference: SSF Libya (Law 13/1980 as amended); PwC Libya Tax 2026
- Social Security Fund: Employee 5.125%, Employer 14.35% (PwC 2026)
  (Law 13/1980 original rates were 3.75%/11.25%)
- Solidarity Fund: 1% of gross (employee); rate read from settings
- PIT: Progressive 5-10% (2 bands)
  Annual: 0-12,000@5%, 12,000+@10%
- Jehad Tax: ABOLISHED effective 14 July 2025 (EY Tax News Update 2025-1651
  "Libya cancels Jihad Tax"; confirmed by Orbitax). Removed from calculator.
  For salary slips dated before 14 July 2025 the tax applied; historical
  computed amounts on submitted slips are preserved as-is.
- Tax year: January 1 - December 31
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

_HARDCODED_PIT_BRACKETS = [
    (0, 12000, 0.05),
    (12000, 0, 0.10),
]


class LibyaCalculator(BaseCalculator):
    """Libya statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. SSF Employee (5.125% PwC 2026)
        ssf_emp_rate = self.settings.ssf_employee_rate
        ssf_emp = gross * (flt(ssf_emp_rate if ssf_emp_rate is not None else 5.125) / 100) if gross > 0 else 0
        results["SSF Employee"] = {
            "amount": ssf_emp, "is_employer_only": False,
        }

        # SSF Employer (14.35% PwC 2026)
        ssf_empr_rate = self.settings.ssf_employer_rate
        ssf_empr = gross * (flt(ssf_empr_rate if ssf_empr_rate is not None else 14.35) / 100) if gross > 0 else 0
        results["SSF Employer"] = {
            "amount": ssf_empr, "is_employer_only": True,
        }

        # 2. Solidarity Fund (rate from settings, default 1%)
        sol_rate = getattr(self.settings, 'solidarity_fund_rate', None)
        solidarity = gross * (flt(sol_rate if sol_rate is not None else 1) / 100) if gross > 0 else 0
        results["Solidarity Fund"] = {
            "amount": solidarity, "is_employer_only": False,
        }

        # 3. PIT
        taxable = max(gross - ssf_emp - solidarity, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        return results

    def _compute_pit(self, taxable_income):
        """PIT progressive bands.

        Reads from settings.pit_bands if populated; falls back to hardcoded bands.

        Annual bands (LYD):
        0 - 12,000: 5%
        12,000+   : 10%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        bands = getattr(self.settings, 'pit_bands', None)
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if annual <= lower:
                    break
                top = upper if upper > 0 else annual
                amount = min(annual, top) - lower
                if amount > 0:
                    tax += amount * rate
            return tax / 12

        # Hardcoded fallback
        tax = 0
        for lower, upper, rate in _HARDCODED_PIT_BRACKETS:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12

