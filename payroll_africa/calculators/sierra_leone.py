"""Sierra Leone statutory deduction calculator.

Reference: NASSIT (National Social Security and Insurance Trust)
- NASSIT: Employee 5%, Employer 10%
- PAYE: Progressive 0-30%
  Annual threshold: SLE 6,000 (500/month) — post-2022 redenomination (1 new Leone = 1000 old)
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
        results["NASSIT Employee"] = {"amount": nassit_emp, "is_employer_only": False}
        results["NASSIT Employer"] = {"amount": nassit_empr, "is_employer_only": True}

        # 2. PAYE
        taxable = max(gross - nassit_emp, 0)
        paye = self._compute_paye(taxable)
        if paye > 0:
            results["PAYE"] = {"amount": paye, "is_employer_only": False}

        return results

    def _get_contribution_base(self, gross):
        ceiling = flt(self.settings.nassit_ceiling or 0)
        if ceiling > 0:
            return min(gross, ceiling) if gross > 0 else 0
        return gross if gross > 0 else 0

    def _compute_paye(self, taxable_income):
        """PAYE progressive.

        Annual bands (SLE, post-2022 redenomination):
        0 - 6,000       : 0%
        6,001 - 12,000  : 15%
        12,001 - 18,000 : 20%
        18,001 - 24,000 : 25%
        Over 24,000     : 30%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        # Read bands from settings if populated; fall back to hardcoded statutory rates.
        bands = getattr(self.settings, "paye_bands", None) or []
        if bands:
            return self._compute_tax_from_bands(annual, bands) / 12

        if annual <= 6000:
            return 0
        tax = 0
        for lower, upper, rate in [
            (6000, 12000, 0.15),
            (12000, 18000, 0.20),
            (18000, 24000, 0.25),
            (24000, 0, 0.30),
        ]:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
