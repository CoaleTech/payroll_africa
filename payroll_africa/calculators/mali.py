"""Mali statutory deduction calculator.

Reference: INSS (Institut National de Securite Sociale), DGI
- INSS Pension: Employee 3.5%, Employer 7.5% (capped)
- AMO Health Insurance: Employee 2%, Employer 3.5% (capped)
- PIT (IR): Progressive 0-35%
- Tax-free threshold: XOF 650,000/year
- Professional deduction: 15% of gross income
- Capped at XOF 8x minimum wage
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class MaliCalculator(BaseCalculator):
    """Mali statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. INSS Pension
        inss_employee = self._compute_inss_employee(gross)
        inss_employer = self._compute_inss_employer(gross)
        results["INSS Pension Employee"] = {
            "amount": inss_employee,
            "is_employer_only": False,
        }
        results["INSS Pension Employer"] = {
            "amount": inss_employer,
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
        taxable = max(gross - inss_employee - amo_employee, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit,
                "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        """Get capped contribution base (XOF 8x minimum wage)."""
        min_wage = flt(self.settings.minimum_wage or 75000)
        ceiling = min_wage * 8
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_inss_employee(self, gross):
        """INSS employee: 3.5% of capped base."""
        rate = flt(self.settings.inss_employee_rate or 3.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_inss_employer(self, gross):
        """INSS employer: 7.5% of capped base."""
        rate = flt(self.settings.inss_employer_rate or 7.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employee(self, gross):
        """AMO employee: 2% of capped base."""
        rate = flt(self.settings.amo_employee_rate or 2) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_amo_employer(self, gross):
        """AMO employer: 3.5% of capped base."""
        rate = flt(self.settings.amo_employer_rate or 3.5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_pit(self, taxable_income):
        """PIT progressive computation.

        Annual bands (XOF):
        0 - 650,000     : 0%
        650,001 - 1,800,000: 13%
        1,800,001 - 4,500,000: 25%
        Over 4,500,000  : 35%
        """
        if taxable_income <= 0:
            return 0

        annual_income = taxable_income * 12
        threshold = flt(self.settings.pit_threshold or 650000)

        if annual_income <= threshold:
            return 0

        tax = 0
        brackets = [
            (650000, 1800000, 0.13),
            (1800000, 4500000, 0.25),
            (4500000, 0, 0.35),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax / 12
