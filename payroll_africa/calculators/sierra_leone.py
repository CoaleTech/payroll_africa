"""Sierra Leone statutory deduction calculator.

Reference: NASSIT (National Social Security and Insurance Trust)
- NASSIT: Employee 5%, Employer 10% (capped)
- PAYE: Progressive 0-30%
  Annual threshold: SLE 36,000,000 (3,000,000/month)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class SierraLeoneCalculator(BaseCalculator):
    """Sierra Leone statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. NASSIT
        base = self._get_contribution_base(gross)
        nassit_emp = base * (flt(self.settings.nassit_employee_rate or 5) / 100)
        nassit_empr = base * (flt(self.settings.nassit_employer_rate or 10) / 100)
        results["NASSIT Employee"] = {
            "amount": nassit_emp, "is_employer_only": False,
        }
        results["NASSIT Employer"] = {
            "amount": nassit_empr, "is_employer_only": True,
        }

        # 2. PAYE
        taxable = max(gross - nassit_emp, 0)
        paye = self._compute_paye(taxable)
        if paye > 0:
            results["PAYE"] = {
                "amount": paye, "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        ceiling = flt(self.settings.nassit_ceiling or 3000000)
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_paye(self, taxable_income):
        """PAYE progressive.

        Annual bands (SLE):
        0 - 36,000,000     : 0%
        36,000,001 - 60,000,000: 15%
        60,000,001 - 120,000,000: 20%
        Over 120,000,000   : 30%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 36000000:
            return 0

        tax = 0
        brackets = [
            (36000000, 60000000, 0.15),
            (60000000, 120000000, 0.20),
            (120000000, 0, 0.30),
        ]
        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
