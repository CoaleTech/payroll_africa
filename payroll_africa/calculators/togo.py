"""Togo statutory deduction calculator.

Reference: CNSS Togo (cnss.tg, CLEISS 2026, CNSS Togo FAQ, auditcomtogo.com)
- Total CNSS: 21.5% (Employee 4%, Employer 17.5%)
  Employer breakdown: Family 3%, Work Injury 2%, Pensions 12.5%
  Employee: Pensions 4%
- INAM health: Employee 5%, Employer 5% (decree 2023-096/PR)
- PIT (IRPP): Progressive 0-35%
  Annual threshold: XOF 900,000 (75,000/month)
- No legal ceiling on CNSS or INAM contributions (cnss_ceiling = 0 means uncapped)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class TogoCalculator(BaseCalculator):
    """Togo statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        base = self._get_contribution_base(gross)

        # 1. CNSS Employee (4% - pension only)
        cnss_emp = base * (self._num("cnss_employee_rate", 4) / 100)
        results["CNSS Employee"] = {"amount": cnss_emp, "is_employer_only": False}

        # 2. CNSS Employer (17.5%)
        cnss_empr = base * (self._num("cnss_employer_rate", 17.5) / 100)
        results["CNSS Employer"] = {"amount": cnss_empr, "is_employer_only": True}

        # 3. INAM health (employee 5%, employer 5%)
        inam_emp = base * (self._num("inam_employee_rate", 5) / 100)
        inam_empr = base * (self._num("inam_employer_rate", 5) / 100)
        results["INAM Employee"] = {"amount": inam_emp, "is_employer_only": False}
        results["INAM Employer"] = {"amount": inam_empr, "is_employer_only": True}

        # 4. PIT
        taxable = max(gross - cnss_emp - inam_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}

        return results

    def _get_contribution_base(self, gross):
        if gross <= 0:
            return 0
        ceiling = flt(self.settings.cnss_ceiling)  # 0 = no ceiling (legal: no cap)
        return min(gross, ceiling) if ceiling > 0 else gross

    def _compute_pit(self, taxable_income):
        """IRPP progressive (annual bands, CGI Togo Art.74, 2026)."""
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        # Read bands from settings if populated; fall back to hardcoded statutory rates.
        bands = getattr(self.settings, "pit_bands", None) or []
        if bands:
            return self._compute_tax_from_bands(annual, bands) / 12

        if annual <= 900000:
            return 0
        tax = 0
        for lower, upper, rate in [
            (900000, 3000000, 0.03),
            (3000000, 6000000, 0.10),
            (6000000, 9000000, 0.15),
            (9000000, 12000000, 0.20),
            (12000000, 15000000, 0.25),
            (15000000, 20000000, 0.30),
            (20000000, 0, 0.35),
        ]:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
