"""Algeria statutory deduction calculator.

Reference: CNAS, DGI
- CNAS Social Security: Employee 9%, Employer ~25.5%
  (Health, maternity, work injury, pension, family allowances)
- PIT (IRG): Progressive 0-35%
  Annual: 0-240k@0%, 240k-480k@20%, 480k-960k@30%, 960k+@35%
- Professional expense deduction: 40% of gross (capped at DZD 24,000/year)
- Tax year: January 1 - December 31
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class AlgeriaCalculator(BaseCalculator):
    """Algeria statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNAS Employee (9%)
        cnas_emp = gross * (flt(self.settings.cnas_employee_rate or 9) / 100) if gross > 0 else 0
        results["CNAS Employee"] = {
            "amount": cnas_emp, "is_employer_only": False,
        }

        # CNAS Employer (~25.5%)
        cnas_empr = gross * (flt(self.settings.cnas_employer_rate or 25.5) / 100) if gross > 0 else 0
        results["CNAS Employer"] = {
            "amount": cnas_empr, "is_employer_only": True,
        }

        # 2. PIT (IRG)
        taxable = max(gross - cnas_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        return results

    def _compute_pit(self, taxable_income):
        """PIT progressive annual bands.

        Annual bands (DZD):
        0 - 240,000      : 0%
        240,001 - 480,000: 20%
        480,001 - 960,000: 30%
        Over 960,000     : 35%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 240000:
            return 0

        tax = 0
        brackets = [
            (240000, 480000, 0.20),
            (480000, 960000, 0.30),
            (960000, 0, 0.35),
        ]
        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
