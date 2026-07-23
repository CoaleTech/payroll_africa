"""Niger statutory deduction calculator.

Reference: CNSS (Caisse Nationale de Securite Sociale), DGI
- CNSS Pension: Employee 5.25%, Employer 8.5% (capped)
- AMO Health: Employee 2.5%, Employer 4.5% (capped)
- PIT (IR): Progressive 0-35%
- Tax-free threshold: XOF 500,000/year
- Professional deduction: 20% of gross
- Contribution ceiling: XOF 8x minimum wage
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class NigerCalculator(BaseCalculator):
    """Niger statutory deduction calculator (2025 rates)."""

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
        min_wage = flt(self.settings.minimum_wage or 70000)
        ceiling = min_wage * 8
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_cnss_employee(self, gross):
        rate = flt(self.settings.cnss_employee_rate or 5.25) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_cnss_employer(self, gross):
        rate = flt(self.settings.cnss_employer_rate or 16.4) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employee(self, gross):
        rate = flt(self.settings.amo_employee_rate or 2.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employer(self, gross):
        rate = flt(self.settings.amo_employer_rate or 4.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_pit(self, taxable_income):
        """ITS progressive computation (monthly barème, Ordonnance N°2025-44)."""
        if taxable_income <= 0:
            return 0
        monthly = taxable_income
        bands = self.settings.pit_bands or []
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if monthly <= lower:
                    break
                top = upper if upper > 0 else monthly
                amount = min(monthly, top) - lower
                if amount > 0:
                    tax += amount * rate
            return tax
        threshold = flt(self.settings.pit_threshold or 25000)
        if monthly <= threshold:
            return 0
        tax = 0
        brackets = [
            (25000, 50000, 0.02),
            (50000, 100000, 0.06),
            (100000, 150000, 0.13),
            (150000, 300000, 0.25),
            (300000, 400000, 0.30),
            (400000, 700000, 0.32),
            (700000, 1000000, 0.34),
            (1000000, 0, 0.35),
        ]
        for lower, upper, rate in brackets:
            if monthly <= lower:
                break
            top = upper if upper > 0 else monthly
            amount = min(monthly, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax
