"""Liberia statutory deduction calculator.

Reference: NASSCorp (National Social Security Corporation)
- NASSCorp: Employee 3%, Employer 4.75% (capped)
- PAYE: Progressive 0-25%
  Annual threshold: LRD 72,000 (6,000/month)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class LiberiaCalculator(BaseCalculator):
    """Liberia statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. NASSCorp
        base = self._get_contribution_base(gross)
        nassc_emp = base * (flt(self.settings.nasscorp_employee_rate or 3) / 100)
        nassc_empr = base * (flt(self.settings.nasscorp_employer_rate or 4.75) / 100)
        results["NASSCorp Employee"] = {
            "amount": nassc_emp, "is_employer_only": False,
        }
        results["NASSCorp Employer"] = {
            "amount": nassc_empr, "is_employer_only": True,
        }

        # 2. PAYE
        taxable = max(gross - nassc_emp, 0)
        paye = self._compute_paye(taxable)
        if paye > 0:
            results["PAYE"] = {
                "amount": paye, "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        ceiling = flt(self.settings.nasscorp_ceiling or 500000)
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_paye(self, taxable_income):
        """PAYE progressive.

        Annual bands (LRD):
        0 - 72,000        : 0%
        72,001 - 180,000  : 5%
        180,001 - 360,000 : 10%
        360,001 - 720,000 : 15%
        720,001 - 1,200,000: 20%
        Over 1,200,000    : 25%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 72000:
            return 0

        tax = 0
        brackets = [
            (72000, 180000, 0.05),
            (180000, 360000, 0.10),
            (360000, 720000, 0.15),
            (720000, 1200000, 0.20),
            (1200000, 0, 0.25),
        ]
        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
