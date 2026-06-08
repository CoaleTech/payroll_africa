"""Seychelles statutory deduction calculator.

Reference: Seychelles Revenue Commission (SRC)
- PAYE: Progressive 0-30%
  Monthly bands:
  0 - 8,555.50 SCR     : 0%
  8,555.51 - 10,027.75 : 15%
  10,027.76 - 13,630   : 20%
  Over 13,630          : 30%
- Social Security (SSCR): Employer 5% (capped)
- No employee social security contribution
- Tax-free threshold: SCR 8,555.50/month
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class SeychellesCalculator(BaseCalculator):
    """Seychelles statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. Social Security - Employer only (5%, capped)
        ss_rate = flt(self.settings.social_security_rate or 5) / 100
        ss_ceiling = flt(self.settings.social_security_ceiling or 15000)
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

        Monthly bands (SCR):
        0 - 8,555.50       : 0%
        8,555.51 - 10,027.75: 15%
        10,027.76 - 13,630 : 20%
        Over 13,630        : 30%
        """
        if gross <= 8555.50:
            return 0

        tax = 0
        brackets = [
            (8555.50, 10027.75, 0.15),
            (10027.75, 13630, 0.20),
            (13630, 0, 0.30),
        ]
        for lower, upper, rate in brackets:
            if gross <= lower:
                break
            top = upper if upper > 0 else gross
            amount = min(gross, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax
