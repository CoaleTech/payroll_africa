"""Togo statutory deduction calculator.

Reference: CNSS Togo (cnss.tg)
- Total CNSS: 21.5% (Employee 4%, Employer 17.5%)
  Employer breakdown: Family 3%, Work Injury 2%, Pensions 12.5%
  Employee: Pensions 4%
- PIT (IRPP): Progressive 0-40%
  Annual threshold: XOF 900,000 (75,000/month)
- Ceiling: typically 8x SMIG
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
        cnss_emp = base * (flt(self.settings.cnss_employee_rate or 4) / 100)
        results["CNSS Employee"] = {
            "amount": cnss_emp, "is_employer_only": False,
        }

        # 2. CNSS Employer (17.5%)
        cnss_empr = base * (flt(self.settings.cnss_employer_rate or 17.5) / 100)
        results["CNSS Employer"] = {
            "amount": cnss_empr, "is_employer_only": True,
        }

        # 2b. INAM health (employee 5%, employer 5%) - decree 2023-096/PR
        inam_emp = base * (flt(self.settings.inam_employee_rate or 5) / 100)
        inam_empr = base * (flt(self.settings.inam_employer_rate or 5) / 100)
        results["INAM Employee"] = {"amount": inam_emp, "is_employer_only": False}
        results["INAM Employer"] = {"amount": inam_empr, "is_employer_only": True}

        # 3. PIT
        taxable = max(gross - cnss_emp - inam_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        ceiling = flt(self.settings.cnss_ceiling or 500000)
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_pit(self, taxable_income):
        """IRPP progressive (annual bands, CGI Togo Art.74, 2026)."""
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 900000:
            return 0
        tax = 0
        brackets = [
            (900000, 3000000, 0.03),
            (3000000, 6000000, 0.10),
            (6000000, 9000000, 0.15),
            (9000000, 12000000, 0.20),
            (12000000, 15000000, 0.25),
            (15000000, 20000000, 0.30),
            (20000000, 0, 0.35),
        ]
        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
