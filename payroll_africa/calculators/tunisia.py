"""Tunisia statutory deduction calculator.

Reference: DGI (Direction Generale des Impots), CNSS
- IRPP: Progressive 0-40% (8 brackets, effective Jan 1, 2025)
- CNSS Employee: 9.18% of gross salary
- CNSS Employer: 17.07% (16.57% for wholly exporting industrial companies)
- Social Solidarity Contribution (SSC): 0.5% (2023-2026)
- Professional expense deduction: 10% of gross (capped at TND 2,000/year)
- Minimum contribution: TND 1/day if tax calculated is less
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class TunisiaCalculator(BaseCalculator):
    """Tunisia statutory deduction calculator (2025/2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNSS Employee contribution (9.18%)
        cnss_employee = self._compute_cnss_employee(gross)
        results["CNSS Employee"] = {
            "amount": cnss_employee,
            "is_employer_only": False,
        }

        # CNSS Employer contribution (17.07%)
        cnss_employer = self._compute_cnss_employer(gross)
        results["CNSS Employer"] = {
            "amount": cnss_employer,
            "is_employer_only": True,
        }

        # 2. Social Solidarity Contribution - Employee (0.5%)
        ssc = self._compute_ssc(gross)
        results["Social Solidarity Contribution"] = {
            "amount": ssc,
            "is_employer_only": False,
        }

        # 3. IRPP (Income Tax) - progressive
        irpp = self._compute_irpp(gross, cnss_employee)
        results["IRPP"] = {
            "amount": irpp,
            "is_employer_only": False,
        }

        return results

    def _compute_cnss_employee(self, gross):
        """CNSS employee: 9.18% of gross salary."""
        rate = flt(self.settings.cnss_employee_rate or 9.18) / 100
        return gross * rate if gross > 0 else 0

    def _compute_cnss_employer(self, gross):
        """CNSS employer: 17.07% of gross (or 16.57% for exporting companies)."""
        is_exporting = self.settings.get("is_exporting_company", 0)
        rate = flt(self.settings.cnss_employer_rate or 17.07) / 100
        if is_exporting:
            rate = flt(self.settings.cnss_employer_export_rate or 16.57) / 100
        return gross * rate if gross > 0 else 0

    def _compute_ssc(self, gross):
        """Social Solidarity Contribution: 0.5% of gross."""
        rate = flt(self.settings.ssc_rate or 0.5) / 100
        return gross * rate if gross > 0 else 0

    def _compute_irpp(self, gross, cnss_employee):
        """Compute IRPP using progressive annual bands.

        Steps:
        1. Deduct CNSS from gross
        2. Apply 10% professional expense deduction (capped at TND 2,000/year)
        3. Apply progressive IRPP brackets

        Annual IRPP brackets (TND, effective 2025):
        0 - 5,000         : 0%
        5,001 - 10,000    : 15%
        10,001 - 20,000   : 25%
        20,001 - 30,000   : 30%
        30,001 - 40,000   : 33%
        40,001 - 50,000   : 36%
        50,001 - 70,000   : 38%
        Over 70,000       : 40%
        """
        if gross <= 0:
            return 0

        # Step 1: Deduct CNSS
        net_after_cnss = gross - cnss_employee

        # Step 2: Professional expense deduction (10%, capped)
        prof_deduction_rate = flt(self.settings.professional_deduction_rate or 10) / 100
        prof_deduction_annual_cap = flt(self.settings.professional_deduction_cap or 2000)
        prof_deduction = min(net_after_cnss * prof_deduction_rate, prof_deduction_annual_cap / 12)

        # Annual taxable income
        taxable_monthly = max(net_after_cnss - prof_deduction, 0)
        taxable_annual = taxable_monthly * 12

        if taxable_annual <= 0:
            return 0

        # Step 3: Progressive IRPP
        tax_annual = self._apply_irpp_bands(taxable_annual)

        return tax_annual / 12

    def _apply_irpp_bands(self, taxable_annual):
        """Apply IRPP progressive bands."""
        tax = 0
        bands = self.settings.irpp_bands or []

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
            tax = self._irpp_hardcoded(taxable_annual)

        return tax

    def _irpp_hardcoded(self, annual_income):
        """Hardcoded 2025 IRPP bands."""
        if annual_income <= 5000:
            return 0

        tax = 0
        brackets = [
            (5000, 10000, 0.15),
            (10000, 20000, 0.25),
            (20000, 30000, 0.30),
            (30000, 40000, 0.33),
            (40000, 50000, 0.36),
            (50000, 70000, 0.38),
            (70000, 0, 0.40),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
