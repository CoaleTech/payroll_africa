"""Benin statutory deduction calculator.

Reference: CNSS, DGI
- CNSS Pension: Employee 3.6%, Employer 6.4% (capped at XOF 8x minimum wage)
- AMO Health: Employee 2%, Employer 4% (capped)
- PIT (IR): Progressive 0-35%
- Tax-free threshold: XOF 500,000/year
- Professional deduction: 20% of gross
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class BeninCalculator(BaseCalculator):
    """Benin statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNSS Pension
        cnss_employee = self._compute_cnss_employee(gross)
        cnss_employer = self._compute_cnss_employer(gross)
        results["CNSS Pension Employee"] = {
            "amount": cnss_employee,
            "is_employer_only": False,
        }
        results["CNSS Pension Employer"] = {
            "amount": cnss_employer,
            "is_employer_only": True,
        }

        # 2. AMO Health Insurance
        amo_employee = self._compute_amo_employee(gross)
        amo_employer = self._compute_amo_employer(gross)
        results["AMO Health Employee"] = {
            "amount": amo_employee,
            "is_employer_only": False,
        }
        results["AMO Health Employer"] = {
            "amount": amo_employer,
            "is_employer_only": True,
        }

        # 3. PIT (IR)
        taxable = max(gross - cnss_employee - amo_employee, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit,
                "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        """Get capped contribution base."""
        min_wage = flt(self.settings.minimum_wage or 65000)
        ceiling = min_wage * 8
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_cnss_employee(self, gross):
        rate = flt(self.settings.cnss_employee_rate or 3.6) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_cnss_employer(self, gross):
        rate = flt(self.settings.cnss_employer_rate or 6.4) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employee(self, gross):
        rate = flt(self.settings.amo_employee_rate or 2) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employer(self, gross):
        rate = flt(self.settings.amo_employer_rate or 4) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_pit(self, taxable_income):
        """PIT progressive.

        Annual bands (XOF):
        0 - 500,000     : 0%
        500,001 - 1,300,000: 10%
        1,300,001 - 3,000,000: 15%
        3,000,001 - 5,000,000: 20%
        5,000,001 - 8,000,000: 25%
        8,000,001 - 12,000,000: 30%
        Over 12,000,000 : 35%
        """
        if taxable_income <= 0:
            return 0

        annual_income = taxable_income * 12
        threshold = flt(self.settings.pit_threshold or 500000)

        if annual_income <= threshold:
            return 0

        tax = 0
        brackets = [
            (500000, 1300000, 0.10),
            (1300000, 3000000, 0.15),
            (3000000, 5000000, 0.20),
            (5000000, 8000000, 0.25),
            (8000000, 12000000, 0.30),
            (12000000, 0, 0.35),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax / 12
