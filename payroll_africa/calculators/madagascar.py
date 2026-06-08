"""Madagascar statutory deduction calculator.

Reference: e-Hetra platform, CNaPS, OSTIE
- IRSA (Impôt sur les Revenus Salariaires et Assimilés): Progressive 0-30%
- CNaPS Social Security: Employee 1% + Employer 13%
- Health Insurance (OSTIE): Employee 1% + Employer 5%
- FMFP (Vocational Training): Employer 1% only
- Contribution ceiling: 8x minimum wage (MGA 262,680/month as of 2024)
  Ceiling = 8 x 262,680 = MGA 2,101,440/month
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class MadagascarCalculator(BaseCalculator):
    """Madagascar statutory deduction calculator (2025/2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNaPS Social Security - Employee (1%)
        cnaps_employee = self._compute_cnaps_employee(gross)
        results["CNaPS Employee"] = {
            "amount": cnaps_employee,
            "is_employer_only": False,
        }

        # CNaPS Social Security - Employer (13%)
        cnaps_employer = self._compute_cnaps_employer(gross)
        results["CNaPS Employer"] = {
            "amount": cnaps_employer,
            "is_employer_only": True,
        }

        # 2. Health Insurance (OSTIE) - Employee (1%)
        health_employee = self._compute_health_employee(gross)
        results["Health Insurance Employee"] = {
            "amount": health_employee,
            "is_employer_only": False,
        }

        # Health Insurance (OSTIE) - Employer (5%)
        health_employer = self._compute_health_employer(gross)
        results["Health Insurance Employer"] = {
            "amount": health_employer,
            "is_employer_only": True,
        }

        # 3. FMFP (Vocational Training) - Employer only (1%)
        fmfp = self._compute_fmfp(gross)
        results["FMFP Training Fund"] = {
            "amount": fmfp,
            "is_employer_only": True,
        }

        # 4. IRSA - progressive income tax
        # Deduct CNaPS employee contribution before tax
        taxable_income = max(gross - cnaps_employee, 0)
        irsa = self._compute_irsa(taxable_income)
        results["IRSA"] = {
            "amount": irsa,
            "is_employer_only": False,
        }

        return results

    def _get_contribution_base(self, gross):
        """Get contribution base capped at 8x minimum wage."""
        min_wage = flt(self.settings.minimum_wage or 262680)
        ceiling_multiplier = flt(self.settings.ceiling_multiplier or 8)
        ceiling = min_wage * ceiling_multiplier
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_cnaps_employee(self, gross):
        """CNaPS employee: 1% of gross, capped."""
        rate = flt(self.settings.cnaps_employee_rate or 1) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_cnaps_employer(self, gross):
        """CNaPS employer: 13% of gross, capped."""
        rate = flt(self.settings.cnaps_employer_rate or 13) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_health_employee(self, gross):
        """Health insurance employee: 1% of gross, capped."""
        rate = flt(self.settings.health_employee_rate or 1) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_health_employer(self, gross):
        """Health insurance employer: 5% of gross, capped."""
        rate = flt(self.settings.health_employer_rate or 5) / 100
        base = self._get_contribution_base(gross)
        return base * rate

    def _compute_fmfp(self, gross):
        """FMFP vocational training: 1% employer only."""
        rate = flt(self.settings.fmfp_rate or 1) / 100
        return gross * rate if gross > 0 else 0

    def _compute_irsa(self, taxable_income):
        """Compute IRSA using progressive monthly bands.

        Monthly taxable income bands (MGA):
        0 - 350,000       : 0%
        350,001 - 400,000 : 5%
        400,001 - 500,000 : 10%
        500,001 - 600,000 : 15%
        600,001 - 800,000 : 20%
        800,001 - 1,000,000: 25%
        Over 1,000,000    : 30%

        Minimum IRSA: MGA 2,000/month
        """
        if taxable_income <= 0:
            return 0

        tax = 0
        bands = self.settings.irsa_bands or []

        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100

                if taxable_income <= lower:
                    break

                band_top = upper if upper > 0 else taxable_income
                taxable_in_band = min(taxable_income, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            tax = self._irsa_hardcoded(taxable_income)

        # Minimum IRSA
        minimum_irsa = flt(self.settings.minimum_irsa or 2000)
        return max(tax, minimum_irsa) if tax > 0 else 0

    def _irsa_hardcoded(self, taxable_income):
        """Hardcoded IRSA bands."""
        if taxable_income <= 350000:
            return 0

        tax = 0
        brackets = [
            (350000, 400000, 0.05),
            (400000, 500000, 0.10),
            (500000, 600000, 0.15),
            (600000, 800000, 0.20),
            (800000, 1000000, 0.25),
            (1000000, 0, 0.30),
        ]

        for lower, upper, rate in brackets:
            if taxable_income <= lower:
                break
            top = upper if upper > 0 else taxable_income
            amount = min(taxable_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
