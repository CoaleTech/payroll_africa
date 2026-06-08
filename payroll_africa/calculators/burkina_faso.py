"""Burkina Faso statutory deduction calculator.

Reference: CNSS, DGI
- CNSS Pension: Employee 5.5%, Employer 9.5% (capped at XOF 8x minimum wage)
- AMO Health: Employee 3%, Employer 5% (capped)
- PIT (IR): Progressive 0-27.5%
- Tax-free threshold: XOF 500,000/year
- Professional deduction: 25% of gross
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class BurkinaFasoCalculator(BaseCalculator):
    """Burkina Faso statutory deduction calculator (2025 rates)."""

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
        rate = flt(self.settings.cnss_employee_rate or 5.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_cnss_employer(self, gross):
        rate = flt(self.settings.cnss_employer_rate or 9.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employee(self, gross):
        rate = flt(self.settings.amo_employee_rate or 3) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employer(self, gross):
        rate = flt(self.settings.amo_employer_rate or 5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_pit(self, taxable_income):
        """PIT progressive.

        Annual bands (XOF):
        0 - 500,000     : 0%
        500,001 - 1,500,000: 12.1%
        1,500,001 - 3,500,000: 18.5%
        3,500,001 - 6,500,000: 25%
        Over 6,500,000  : 27.5%
        """
        if taxable_income <= 0:
            return 0

        annual_income = taxable_income * 12
        threshold = flt(self.settings.pit_threshold or 500000)

        if annual_income <= threshold:
            return 0

        tax = 0
        brackets = [
            (500000, 1500000, 0.121),
            (1500000, 3500000, 0.185),
            (3500000, 6500000, 0.25),
            (6500000, 0, 0.275),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax / 12
