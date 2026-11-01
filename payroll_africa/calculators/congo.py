"""Congo (Brazzaville) statutory deduction calculator.

Reference: CNSS Congo, CNAMGS
- CNSS: Employer 16% of gross salary
  Components: Family allowances, old age pension, work injury
- CNAMGS (Health): Employer 4.1% of gross salary
  (Caisse Nationale d'Assurance Maladie et de Garantie Sociale)
- Employee contribution: Typically minimal or 0%
- PIT: Progressive tax system
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class CongoCalculator(BaseCalculator):
    """Congo (Brazzaville) statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNSS - Employer only (16%)
        cnss_rate = flt(self.settings.cnss_rate or 20.285) / 100
        cnss_ceiling = flt(self.settings.cnss_ceiling or 1200000)
        cnss_base = min(gross, cnss_ceiling) if gross > 0 else 0
        cnss_empr = cnss_base * cnss_rate
        results["CNSS Employer"] = {
            "amount": cnss_empr,
            "is_employer_only": True,
        }

        # 2. CNSS - Employee contribution (~4%)
        cnss_employee = self._compute_cnss_employee(gross)
        results["CNSS Employee"] = {
            "amount": cnss_employee,
            "is_employer_only": False,
        }

        # 3. CAMU Health - Employer only (0.5% on income > 500,000)
        camu_rate = flt(self.settings.cnamgs_rate or 0.5) / 100
        camu_base = max(gross - 500000, 0) if gross > 0 else 0
        camu_empr = camu_base * camu_rate
        results["CAMU Health Employer"] = {
            "amount": camu_empr,
            "is_employer_only": True,
        }

        # 4. PIT - progressive on net of CNSS employee
        taxable = max(gross - cnss_employee, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit,
                "is_employer_only": False,
            }

        return results

    def _compute_cnss_employee(self, gross):
        """Employee CNSS contribution (~4%), capped at cnss_ceiling (default 1,200,000 XAF)."""
        rate = flt(self.settings.cnss_employee_rate or 4) / 100
        ceiling = flt(self.settings.cnss_ceiling or 1200000)
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_pit(self, taxable_income):
        """PIT progressive (annual XAF bands).

        0 - 900,000      : 0%
        900,001 - 2,400,000 : 5%
        2,400,001 - 6,000,000 : 10%
        6,000,001 - 12,000,000: 15%
        12,000,001 - 24,000,000: 25%
        Over 24,000,000  : 35%

        Reads pit_bands from settings if populated; falls back to hardcoded.
        """
        if taxable_income <= 0:
            return 0

        annual = taxable_income * 12
        if annual <= 900000:
            return 0

        bands = getattr(self.settings, "pit_bands", None) or []
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if annual <= lower:
                    break
                band_top = upper if upper > 0 else annual
                amount = min(annual, band_top) - lower
                if amount > 0:
                    tax += amount * rate
            return tax / 12

        # Hardcoded fallback
        tax = 0
        brackets = [
            (900000, 2400000, 0.05),
            (2400000, 6000000, 0.10),
            (6000000, 12000000, 0.15),
            (12000000, 24000000, 0.25),
            (24000000, 0, 0.35),
        ]

        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax / 12
