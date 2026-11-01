"""Guinea (Conakry) statutory deduction calculator.

Reference: INSS Guinea (Institut National de Securite Sociale), DGI
- INSS Pension: Employee 5%, Employer 1.5%
- INSS Family Allowances: Employer 6%
- INSS Work Injury: Employer 4% flat (all risk classes)
- AMO Health: Employee 0%, Employer 6.5%
- PIT: Progressive 0-40%
- Contribution ceiling: GNF 2,500,000/month (fixed statutory ceiling)
- Minimum wage (SMIG): GNF 550,000/month (Decree D/2022/0270/PRG/SGG)

Sources: cnss.gov.gn/cotisations-sociales-employeurs; walirh.com 2026; mahkano 2026
"""

from payroll_africa.calculators.base import BaseCalculator


class GuineaCalculator(BaseCalculator):
    """Guinea statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        base = self._get_contribution_base(gross)

        # 1. INSS Pension
        pension_emp = base * (self._num("inss_pension_employee_rate", 5) / 100)
        pension_empr = base * (self._num("inss_pension_employer_rate", 1.5) / 100)
        results["INSS Pension Employee"] = {"amount": pension_emp, "is_employer_only": False}
        results["INSS Pension Employer"] = {"amount": pension_empr, "is_employer_only": True}

        # 2. INSS Family Allowances - Employer only
        family = base * (self._num("inss_family_rate", 6) / 100)
        results["INSS Family Allowances"] = {"amount": family, "is_employer_only": True}

        # 3. Work Injury - Employer only, 4% flat (all risk classes; field kept for info)
        injury = base * 0.04 if base > 0 else 0
        results["Work Injury Insurance"] = {"amount": injury, "is_employer_only": True}

        # 4. AMO Health
        amo_emp = base * (self._num("amo_employee_rate", 0) / 100)
        amo_empr = base * (self._num("amo_employer_rate", 6.5) / 100)
        results["AMO Health Employee"] = {"amount": amo_emp, "is_employer_only": False}
        results["AMO Health Employer"] = {"amount": amo_empr, "is_employer_only": True}

        # 5. PIT
        taxable = max(gross - pension_emp - amo_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}

        return results

    def _get_contribution_base(self, gross):
        """Contribution base capped at the fixed statutory ceiling (GNF 2,500,000/month)."""
        ceiling = self._num("inss_ceiling", 0) or 2500000
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_pit(self, taxable_income):
        """PIT progressive.

        Annual bands (GNF):
        0 - 1,200,000        : 0%
        1,200,001 - 3,000,000: 5%
        3,000,001 - 6,000,000: 12%
        6,000,001 - 12,000,000: 20%
        12,000,001 - 24,000,000: 30%
        Over 24,000,000      : 40%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        # Read bands from settings if populated; fall back to hardcoded statutory rates.
        bands = getattr(self.settings, "pit_bands", None) or []
        if bands:
            return self._compute_tax_from_bands(annual, bands) / 12

        if annual <= 1200000:
            return 0
        tax = 0
        for lower, upper, rate in [
            (1200000, 3000000, 0.05),
            (3000000, 6000000, 0.12),
            (6000000, 12000000, 0.20),
            (12000000, 24000000, 0.30),
            (24000000, 0, 0.40),
        ]:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
