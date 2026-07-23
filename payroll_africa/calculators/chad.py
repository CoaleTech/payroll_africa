"""Chad statutory deduction calculator.

Reference: CNPS Chad, ONPT (Organisme National de Prevoyance et de Retraite)
- CNPS Pension: Employee 3.5%, Employer 7%
- CNPS Family Allowances: Employer 7.5%
- CNPS Work Injury: Employer 2-5% by risk
- PIT: Progressive 0-30%
- Ceiling: XAF 8x minimum wage
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class ChadCalculator(BaseCalculator):
    """Chad statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        base = self._get_contribution_base(gross)

        # 1. CNPS Pension
        pension_emp = base * (flt(self.settings.cnps_pension_employee_rate or 3.5) / 100)
        pension_empr = base * (flt(self.settings.cnps_pension_employer_rate or 7) / 100)
        results["CNPS Pension Employee"] = {
            "amount": pension_emp, "is_employer_only": False,
        }
        results["CNPS Pension Employer"] = {
            "amount": pension_empr, "is_employer_only": True,
        }

        # 2. CNPS Family Allowances - Employer only
        family = base * (flt(self.settings.cnps_family_rate or 7.5) / 100)
        results["CNPS Family Allowances"] = {
            "amount": family, "is_employer_only": True,
        }

        # 3. Work Injury - Employer only
        risk_class = flt(self.settings.work_injury_risk_class or 1)
        risk_rates = {1: 2.0, 2: 3.0, 3: 5.0}
        injury = gross * (risk_rates.get(int(risk_class), 2.0) / 100) if gross > 0 else 0
        results["Work Injury Insurance"] = {
            "amount": injury, "is_employer_only": True,
        }

        # 4. PIT
        taxable = max(gross - pension_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        min_wage = flt(self.settings.minimum_wage or 75000)
        ceiling = min_wage * 8
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_pit(self, taxable_income):
        """PIT progressive.

        Annual bands (XAF):
        0 - 900,000      : 0%
        900,001 - 2,400,000: 5%
        2,400,001 - 6,000,000: 10%
        6,000,001 - 12,000,000: 15%
        12,000,001 - 24,000,000: 20%
        24,000,001 - 48,000,000: 25%
        Over 48,000,000  : 30%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 800000:
            return 0

        tax = 0
        brackets = [
            (800000, 6000000, 0.105),
            (6000000, 7500000, 0.15),
            (7500000, 9000000, 0.20),
            (9000000, 12000000, 0.25),
            (12000000, 0, 0.30),
        ]
        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
