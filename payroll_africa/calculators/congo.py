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
        cnss_rate = flt(self.settings.cnss_rate or 16) / 100
        cnss_ceiling = flt(self.settings.cnss_ceiling or 1500000)
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

        # 3. CNAMGS Health - Employer only (4.1%)
        cnamgs_rate = flt(self.settings.cnamgs_rate or 4.1) / 100
        cnamgs_base = min(gross, cnss_ceiling) if gross > 0 else 0
        cnamgs_empr = cnamgs_base * cnamgs_rate
        results["CNAMGS Health Employer"] = {
            "amount": cnamgs_empr,
            "is_employer_only": True,
        }

        # 4. PIT - progressive
        pit = self._compute_pit(gross)
        if pit > 0:
            results["PIT"] = {
                "amount": pit,
                "is_employer_only": False,
            }

        return results

    def _compute_cnss_employee(self, gross):
        """Employee CNSS contribution (~4%), same ceiling as employer."""
        rate = flt(self.settings.cnss_employee_rate or 4) / 100
        ceiling = flt(self.settings.cnss_ceiling or 1500000)
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_pit(self, gross):
        """PIT progressive.

        Annual bands (XAF):
        0 - 900,000      : 0%
        900,001 - 2,400,000 : 5%
        2,400,001 - 6,000,000 : 10%
        6,000,001 - 12,000,000: 15%
        12,000,001 - 24,000,000: 25%
        Over 24,000,000  : 35%
        """
        if gross <= 0:
            return 0

        annual = gross * 12
        if annual <= 900000:
            return 0

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
