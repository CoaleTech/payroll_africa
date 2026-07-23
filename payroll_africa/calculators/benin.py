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
        ceiling = flt(self.settings.cnss_ceiling or 0)
        if ceiling > 0:
            return min(gross, ceiling) if gross > 0 else 0
        return gross if gross > 0 else 0

    def _compute_cnss_employee(self, gross):
        rate = flt(self.settings.cnss_employee_rate or 3.6) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_cnss_employer(self, gross):
        rate = flt(self.settings.cnss_employer_rate or 15.4) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employee(self, gross):
        rate = flt(self.settings.amo_employee_rate or 0) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employer(self, gross):
        rate = flt(self.settings.amo_employer_rate or 0) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_pit(self, taxable_income):
        """ITS progressive (monthly bands, CGI Benin 2026)."""
        if taxable_income <= 0:
            return 0
        threshold = flt(self.settings.pit_threshold or 60000)
        if taxable_income <= threshold:
            return 0
        tax = 0
        brackets = [
            (60000, 150000, 0.10),
            (150000, 250000, 0.15),
            (250000, 500000, 0.19),
            (500000, 1000000, 0.30),
            (1000000, 0, 0.40),
        ]
        for lower, upper, rate in brackets:
            if taxable_income <= lower:
                break
            top = upper if upper > 0 else taxable_income
            amount = min(taxable_income, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax
