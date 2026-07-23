"""Egypt statutory deduction calculator.

Reference: Egyptian Tax Authority (ETA), NOSI
- Social Insurance: Employee 11%, Employer 18.75% (capped at EGP 16,700/month as of 2026)
- Health Insurance: Employee 1%, Employer 3.25% (no cap)
- Martyrs Fund: 0.05% of gross (employee)
- PIT: Progressive 0-27.5% on annual income
- Personal exemption: EGP 15,000/year
- Dependent deduction: EGP 3,000 per dependent (max 2 children + spouse)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class EgyptCalculator(BaseCalculator):
    """Egypt statutory deduction calculator (2025/2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. Social Insurance - Employee (11%, capped)
        social_insurance_emp = self._compute_social_insurance_employee(gross)
        results["Social Insurance Employee"] = {
            "amount": social_insurance_emp,
            "is_employer_only": False,
        }

        # Social Insurance - Employer (18.75%, capped)
        social_insurance_empr = self._compute_social_insurance_employer(gross)
        results["Social Insurance Employer"] = {
            "amount": social_insurance_empr,
            "is_employer_only": True,
        }

        # 2. Health Insurance - Employee (1%, no cap)
        health_emp = self._compute_health_insurance_employee(gross)
        results["Health Insurance Employee"] = {
            "amount": health_emp,
            "is_employer_only": False,
        }

        # Health Insurance - Employer (3.25%, no cap)
        health_empr = self._compute_health_insurance_employer(gross)
        results["Health Insurance Employer"] = {
            "amount": health_empr,
            "is_employer_only": True,
        }

        # 3. Martyrs Fund - Employee (0.05%)
        martyrs = gross * 0.0005 if gross > 0 else 0
        results["Martyrs Fund"] = {
            "amount": martyrs,
            "is_employer_only": False,
        }

        # 4. Income Tax - progressive
        annual_deductions = (social_insurance_emp + health_emp + martyrs) * 12
        personal_exemption = flt(self.settings.personal_exemption or 20000)   # PwC 2024 (Law 7/2024)
        dependent_deduction = self._get_dependent_deduction()

        taxable_annual = max(gross * 12 - annual_deductions - personal_exemption - dependent_deduction, 0)
        income_tax = self._compute_income_tax(taxable_annual)
        results["Income Tax"] = {
            "amount": income_tax / 12,
            "is_employer_only": False,
        }

        return results

    def _compute_social_insurance_employee(self, gross):
        """Employee social insurance: 11% of gross, capped."""
        ceiling = flt(self.settings.social_insurance_ceiling or 16700)
        rate = flt(self.settings.social_insurance_employee_rate or 11) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_social_insurance_employer(self, gross):
        """Employer social insurance: 18.75% of gross, capped."""
        ceiling = flt(self.settings.social_insurance_ceiling or 16700)
        rate = flt(self.settings.social_insurance_employer_rate or 18.75) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_health_insurance_employee(self, gross):
        """Employee health insurance: 1% of gross, no cap."""
        rate = flt(self.settings.health_insurance_employee_rate or 1) / 100
        return gross * rate if gross > 0 else 0

    def _compute_health_insurance_employer(self, gross):
        """Employer health insurance: 3.25% of gross, no cap."""
        rate = flt(self.settings.health_insurance_employer_rate or 3.25) / 100
        return gross * rate if gross > 0 else 0

    def _get_dependent_deduction(self):
        """Get dependent deduction: EGP 3,000 per dependent."""
        num_dependents = flt(self.settings.number_of_dependents or 0)
        max_dependents = flt(self.settings.max_dependents or 3)
        deduction_per_dependent = flt(self.settings.dependent_deduction or 3000)
        actual = min(num_dependents, max_dependents)
        return actual * deduction_per_dependent

    def _compute_income_tax(self, taxable_annual):
        """Compute income tax using progressive annual bands.

        Annual taxable income bands (EGP):
        0 - 40,000        : 0%
        40,001 - 55,000   : 10%
        55,001 - 70,000   : 15%
        70,001 - 200,000  : 20%
        200,001 - 400,000 : 22.5%
        400,001 - 1,200,000: 25%
        Over 1,200,000    : 27.5%
        """
        if taxable_annual <= 0:
            return 0

        tax = 0
        bands = self.settings.income_tax_bands or []

        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100

                if taxable_annual <= lower:
                    break

                band_top = upper if upper > 0 else taxable_annual
                taxable_in_band = min(taxable_annual, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            tax = self._tax_hardcoded(taxable_annual)

        return tax

    def _tax_hardcoded(self, annual_income):
        """Hardcoded income tax bands."""
        if annual_income <= 40000:
            return 0

        tax = 0
        brackets = [
            (40000, 55000, 0.10),
            (55000, 70000, 0.15),
            (70000, 200000, 0.20),
            (200000, 400000, 0.225),
            (400000, 1200000, 0.25),
            (1200000, 0, 0.275),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
