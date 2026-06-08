"""Senegal statutory deduction calculator.

Reference: IPRES, CSS, DGI
- IPRES (Pension): Employee 5.6%, Employer 8.4%
  Capped at 4x minimum wage (SMIG XOF 74,750/month as of 2025)
  Ceiling = 4 x 74,750 = XOF 299,000/month
- CSS Health Insurance: Employee ~3%, Employer ~5% (capped)
- AMO Health: 6% total (3% employee + 3% employer) - for companies with >20 employees
- PIT (IR): Progressive 0-40% with multiple brackets
- Tax-free threshold: XOF 630,000/year (XOF 52,500/month)
- Family deductions: XOF 100,000 per dependent child
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class SenegalCalculator(BaseCalculator):
    """Senegal statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. IPRES Pension - Employee (5.6%, capped)
        ipres_employee = self._compute_ipres_employee(gross)
        results["IPRES Pension Employee"] = {
            "amount": ipres_employee,
            "is_employer_only": False,
        }

        # IPRES Pension - Employer (8.4%, capped)
        ipres_employer = self._compute_ipres_employer(gross)
        results["IPRES Pension Employer"] = {
            "amount": ipres_employer,
            "is_employer_only": True,
        }

        # 2. CSS Health Insurance - Employee (~3%, capped)
        css_employee = self._compute_css_employee(gross)
        if css_employee > 0:
            results["CSS Health Employee"] = {
                "amount": css_employee,
                "is_employer_only": False,
            }

        # CSS Health Insurance - Employer (~5%, capped)
        css_employer = self._compute_css_employer(gross)
        if css_employer > 0:
            results["CSS Health Employer"] = {
                "amount": css_employer,
                "is_employer_only": True,
            }

        # 3. AMO Health (for companies >20 employees) - 6% total
        amo_employee = self._compute_amo_employee(gross)
        amo_employer = self._compute_amo_employer(gross)
        if amo_employee > 0 and amo_employer > 0:
            results["AMO Health Employee"] = {
                "amount": amo_employee,
                "is_employer_only": False,
            }
            results["AMO Health Employer"] = {
                "amount": amo_employer,
                "is_employer_only": True,
            }

        # 4. Income Tax (IR) - progressive
        taxable_income = max(gross - ipres_employee - css_employee - amo_employee, 0)
        income_tax = self._compute_income_tax(taxable_income)
        if income_tax > 0:
            results["Income Tax"] = {
                "amount": income_tax,
                "is_employer_only": False,
            }

        return results

    def _get_ipres_ceiling(self):
        """Get IPRES ceiling based on minimum wage."""
        min_wage = flt(self.settings.minimum_wage or 74750)
        ceiling_multiplier = flt(self.settings.ipres_ceiling_multiplier or 4)
        return min_wage * ceiling_multiplier

    def _compute_ipres_employee(self, gross):
        """IPRES employee: 5.6% of gross, capped."""
        ceiling = flt(self.settings.ipres_ceiling or 299000)
        rate = flt(self.settings.ipres_employee_rate or 5.6) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_ipres_employer(self, gross):
        """IPRES employer: 8.4% of gross, capped."""
        ceiling = flt(self.settings.ipres_ceiling or 299000)
        rate = flt(self.settings.ipres_employer_rate or 8.4) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_css_employee(self, gross):
        """CSS health employee: ~3% of gross, capped."""
        ceiling = flt(self.settings.css_ceiling or 299000)
        rate = flt(self.settings.css_employee_rate or 3) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_css_employer(self, gross):
        """CSS health employer: ~5% of gross, capped."""
        ceiling = flt(self.settings.css_ceiling or 299000)
        rate = flt(self.settings.css_employer_rate or 5) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_amo_employee(self, gross):
        """AMO health employee: 3% of gross (if applicable)."""
        if not self.settings.get("amo_applicable"):
            return 0
        rate = flt(self.settings.amo_employee_rate or 3) / 100
        ceiling = flt(self.settings.amo_ceiling or 299000)
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_amo_employer(self, gross):
        """AMO health employer: 3% of gross (if applicable)."""
        if not self.settings.get("amo_applicable"):
            return 0
        rate = flt(self.settings.amo_employer_rate or 3) / 100
        ceiling = flt(self.settings.amo_ceiling or 299000)
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_income_tax(self, taxable_income):
        """Compute income tax using progressive annual bands.

        Annual taxable income bands (XOF):
        0 - 630,000      : 0%
        630,001 - 1,500,000 : 20%
        1,500,001 - 4,000,000 : 30%
        1,500,001 - 4,000,000 : 30%
        4,000,001 - 8,000,000 : 35%
        8,000,001 - 13,500,000 : 37%
        Over 13,500,000 : 40%

        Monthly threshold: XOF 52,500
        """
        if taxable_income <= 0:
            return 0

        annual_income = taxable_income * 12
        threshold = flt(self.settings.tax_free_threshold_annual or 630000)

        if annual_income <= threshold:
            return 0

        tax = 0
        bands = self.settings.income_tax_bands or []

        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if annual_income <= lower:
                    break
                band_top = upper if upper > 0 else annual_income
                taxable_in_band = min(annual_income, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            tax = self._tax_hardcoded(annual_income, threshold)

        # Family deductions
        num_children = flt(self.settings.number_of_dependent_children or 0)
        max_children = flt(self.settings.max_deductible_children or 6)
        deduction_per_child = flt(self.settings.child_deduction or 100000)
        actual_children = min(num_children, max_children)
        tax = max(tax - (actual_children * deduction_per_child), 0)

        return tax / 12

    def _tax_hardcoded(self, annual_income, threshold):
        """Hardcoded income tax bands for Senegal."""
        if annual_income <= threshold:
            return 0

        tax = 0
        brackets = [
            (630000, 1500000, 0.20),
            (1500000, 4000000, 0.30),
            (4000000, 8000000, 0.35),
            (8000000, 13500000, 0.37),
            (13500000, 0, 0.40),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
