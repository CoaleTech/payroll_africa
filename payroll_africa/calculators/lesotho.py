"""Lesotho statutory deduction calculator.

Reference: LRA (Lesotho Revenue Authority)
- PAYE: Progressive 0-30%
  Annual: 0-74,040@20% (with credit), 74,040+@30%
  Monthly credit: M 970
- No mandatory national social security (FNPF is voluntary)
- Pension contributions to approved funds: deductible up to 20%
- Tax year: April 1 - March 31
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class LesothoCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        paye = self._compute_paye(gross)
        if paye > 0:
            results["PAYE"] = {"amount": paye, "is_employer_only": False}
        return results

    def _compute_paye(self, gross):
        """Compute monthly PAYE for Lesotho.

        If ``tax_free_threshold`` (annual LSL) is set on settings and annual
        income falls at or below it, return 0.  Default bands: 0–74,040 @ 20 %,
        above @ 30 %.  Annual tax credit (default 11,640 LSL) reduces raw tax
        before dividing by 12.
        """
        if gross <= 0:
            return 0
        annual = gross * 12

        threshold = getattr(self.settings, "tax_free_threshold", None) or 0
        if threshold and annual <= flt(threshold):
            return 0

        credit = flt(self.settings.tax_credit_annual or 11640)

        if annual <= 74040:
            tax = annual * 0.20
        else:
            tax = 14808 + (annual - 74040) * 0.30

        return max(tax - credit, 0) / 12
