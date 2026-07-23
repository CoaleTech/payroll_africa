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
        """Mali social contributions are uncapped (INPS on total salary)."""
        return gross if gross > 0 else 0

    def _compute_inss_employee(self, gross):
        """INSS employee: 3.5% of capped base."""
        rate = flt(self.settings.inss_employee_rate or 3.6) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_inss_employer(self, gross):
        """INSS employer: 8.4% of capped base."""
        rate = flt(self.settings.inss_employer_rate or 5.4) / 100
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
        """ITS progressive computation (monthly barème, DGI Mali 2025)."""
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
        threshold = flt(self.settings.pit_threshold or 175000)
        if monthly <= threshold:
            return 0
        tax = 0
        brackets = [
            (175000, 600000, 0.05),
            (600000, 1200000, 0.13),
            (1200000, 1800000, 0.20),
            (1800000, 2400000, 0.28),
            (2400000, 3500000, 0.34),
            (3500000, 0, 0.40),
        ]
        for lower, upper, rate in brackets:
            if monthly <= lower:
                break
            top = upper if upper > 0 else monthly
            amount = min(monthly, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax
