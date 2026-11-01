"""Liberia statutory deduction calculator.

Reference: NASSCorp (National Social Security Corporation)
- NASSCorp: Employee 4%, Employer 6% (uncapped; ceiling=0 means no cap)
- PAYE: Progressive 0-25%
  Annual threshold: LRD 70,000 (≈5,833/month)
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
        nassc_emp = base * (flt(self.settings.nasscorp_employee_rate or 4) / 100)
        nassc_empr = base * (flt(self.settings.nasscorp_employer_rate or 6) / 100)
        results["NASSCorp Employee"] = {"amount": nassc_emp, "is_employer_only": False}
        results["NASSCorp Employer"] = {"amount": nassc_empr, "is_employer_only": True}

        # 2. PAYE
        taxable = max(gross - nassc_emp, 0)
        paye = self._compute_paye(taxable)
        if paye > 0:
            results["PAYE"] = {"amount": paye, "is_employer_only": False}

        return results

    def _get_contribution_base(self, gross):
        ceiling = flt(self.settings.nasscorp_ceiling or 0)
        if ceiling > 0:
            return min(gross, ceiling) if gross > 0 else 0
        return gross if gross > 0 else 0

    def _compute_paye(self, taxable_income):
        """PAYE progressive.

        Annual bands (LRD):
        0 - 70,000         : 0%
        70,001 - 200,000   : 5%
        200,001 - 800,000  : 15%
        Over 800,000       : 25%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        # Read bands from settings if populated; fall back to hardcoded statutory rates.
        bands = getattr(self.settings, "paye_bands", None) or []
        if bands:
            return self._compute_tax_from_bands(annual, bands) / 12

        if annual <= 70000:
            return 0
        tax = 0
        for lower, upper, rate in [
            (70000, 200000, 0.05),
            (200000, 800000, 0.15),
            (800000, 0, 0.25),
        ]:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
