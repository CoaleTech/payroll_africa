"""Guinea (Conakry) statutory deduction calculator.

Reference: INSS Guinea (Institut National de Securite Sociale), DGI
- INSS Pension: Employee 2.5%, Employer 5%
- INSS Family Allowances: Employer 3%
- INSS Work Injury: Employer 1.5-4% by risk class
- AMO Health: 3% total (employee + employer split)
- PIT: Progressive 0-40%
- Contribution ceiling: typically 8x minimum wage
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class GuineaCalculator(BaseCalculator):
    """Guinea statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        base = self._get_contribution_base(gross)

        # 1. INSS Pension
        pension_emp = base * (flt(self.settings.inss_pension_employee_rate or 2.5) / 100)
        pension_empr = base * (flt(self.settings.inss_pension_employer_rate or 5) / 100)
        results["INSS Pension Employee"] = {
            "amount": pension_emp, "is_employer_only": False,
        }
        results["INSS Pension Employer"] = {
            "amount": pension_empr, "is_employer_only": True,
        }

        # 2. INSS Family Allowances - Employer only
        family = base * (flt(self.settings.inss_family_rate or 3) / 100)
        results["INSS Family Allowances"] = {
            "amount": family, "is_employer_only": True,
        }

        # 3. Work Injury - Employer only
        risk_class = flt(self.settings.work_injury_risk_class or 1)
        risk_rates = {1: 1.5, 2: 2.5, 3: 4.0}
        injury_rate = risk_rates.get(int(risk_class), 1.5) / 100
        injury = gross * injury_rate if gross > 0 else 0
        results["Work Injury Insurance"] = {
            "amount": injury, "is_employer_only": True,
        }

        # 4. AMO Health
        amo_emp = base * (flt(self.settings.amo_employee_rate or 1.5) / 100)
        amo_empr = base * (flt(self.settings.amo_employer_rate or 1.5) / 100)
        results["AMO Health Employee"] = {
            "amount": amo_emp, "is_employer_only": False,
        }
        results["AMO Health Employer"] = {
            "amount": amo_empr, "is_employer_only": True,
        }

        # 5. PIT
        taxable = max(gross - pension_emp - amo_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        min_wage = flt(self.settings.minimum_wage or 80000)
        ceiling = min_wage * 8
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_pit(self, taxable_income):
        """PIT progressive.

        Annual bands (GNF):
        0 - 1,200,000     : 0%
        1,200,001 - 3,000,000: 5%
        3,000,001 - 6,000,000: 12%
        6,000,001 - 12,000,000: 20%
        12,000,001 - 24,000,000: 30%
        Over 24,000,000   : 40%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 1200000:
            return 0

        tax = 0
        brackets = [
            (1200000, 3000000, 0.05),
            (3000000, 6000000, 0.12),
            (6000000, 12000000, 0.20),
            (12000000, 24000000, 0.30),
            (24000000, 0, 0.40),
        ]
        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
