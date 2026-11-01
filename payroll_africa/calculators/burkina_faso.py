"""Burkina Faso statutory deduction calculator.

Reference: CNSS, DGI
- CNSS Pension: Employee 8%, Employer 17.5% (capped at cnss_ceiling, default 800,000 XOF)
- AMO Health: Employee 2.5%, Employer 2.5% (same ceiling)
- PIT (IUTS): Progressive 0-25% on monthly taxable income
- Tax-free threshold: XOF 30,000/month
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
        ceiling = flt(self.settings.cnss_ceiling or 800000)
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_cnss_employee(self, gross):
        rate = self._num("cnss_employee_rate", 8) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_cnss_employer(self, gross):
        rate = self._num("cnss_employer_rate", 17.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employee(self, gross):
        rate = self._num("amo_employee_rate", 2.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employer(self, gross):
        rate = self._num("amo_employer_rate", 2.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_pit(self, taxable_income):
        """IUTS progressive (monthly bands, DGI Burkina Faso)."""
        if taxable_income <= 0:
            return 0
        threshold = self._num("pit_threshold", 30000)
        if taxable_income <= threshold:
            return 0
        tax = 0
        brackets = [
            (30000, 50000, 0.121),
            (50000, 80000, 0.139),
            (80000, 120000, 0.157),
            (120000, 170000, 0.184),
            (170000, 250000, 0.217),
            (250000, 0, 0.25),
        ]
        for lower, upper, rate in brackets:
            if taxable_income <= lower:
                break
            top = upper if upper > 0 else taxable_income
            amount = min(taxable_income, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax
