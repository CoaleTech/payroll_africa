"""Guinea-Bissau statutory deduction calculator.

Reference: INSS Guinea-Bissau
- INSS: Employee 8%, Employer 14%
  Ceiling: 8x minimum wage (inss_ceiling field overrides when non-zero)
- PIT (IRPS): Progressive 1-20% (no exempt band; 1% from first franc)
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class GuineaBissauCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        min_wage = flt(self.settings.minimum_wage or 45000)
        # inss_ceiling overrides min_wage*8 when explicitly set (non-zero)
        inss_ceiling = flt(getattr(self.settings, "inss_ceiling", None) or 0)
        ceiling = inss_ceiling if inss_ceiling > 0 else min_wage * 8
        base = min(gross, ceiling) if gross > 0 else 0

        inss_emp = base * (flt(self.settings.inss_employee_rate or 8) / 100)
        inss_empr = base * (flt(self.settings.inss_employer_rate or 14) / 100)
        results["INSS Employee"] = {"amount": inss_emp, "is_employer_only": False}
        results["INSS Employer"] = {"amount": inss_empr, "is_employer_only": True}

        taxable = max(gross - inss_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        """IRPS progressive.

        Annual bands (XOF) — no exempt band, 1% from the first franc:
        0 - 500,000         : 1%
        500,001 - 1,000,000 : 6%
        1,000,001 - 2,500,000: 8%
        2,500,001 - 3,600,000: 10%
        3,600,001 - 4,806,000: 12%
        4,806,001 - 9,000,000: 14%
        9,000,001 - 13,200,000: 16%
        13,200,001 - 18,000,000: 18%
        Over 18,000,000     : 20%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        # Read bands from settings if populated; fall back to hardcoded statutory rates.
        bands = getattr(self.settings, "pit_bands", None) or []
        if bands:
            return self._compute_tax_from_bands(annual, bands) / 12

        tax = 0
        for lower, upper, rate in [
            (0, 500000, 0.01),
            (500000, 1000000, 0.06),
            (1000000, 2500000, 0.08),
            (2500000, 3600000, 0.10),
            (3600000, 4806000, 0.12),
            (4806000, 9000000, 0.14),
            (9000000, 13200000, 0.16),
            (13200000, 18000000, 0.18),
            (18000000, 0, 0.20),
        ]:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
