"""Libya statutory deduction calculator.

Reference: SSF Libya (Law 13/1980)
- Social Security Fund: Employee 3.75%, Employer 11.25%, State 0.75%
- Solidarity Fund: 1% of gross (employee)
- PIT: Progressive 5-10% (2 bands)
  Annual: 0-12,000@5%, 12,000+@10%
- Jehad Tax: 1-3% based on monthly income
  < LYD 50/month: 1%
  LYD 50-100/month: 2%
  > LYD 100/month: 3%
- Minimum wage: LYD 1,000/month (Jan 2025)
- Tax year: January 1 - December 31
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class LibyaCalculator(BaseCalculator):
    """Libya statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. SSF Employee (5.125%, PwC 2026)
        ssf_emp = gross * (flt(self.settings.ssf_employee_rate or 5.125) / 100) if gross > 0 else 0
        results["SSF Employee"] = {
            "amount": ssf_emp, "is_employer_only": False,
        }

        # SSF Employer (14.35%, Libyan entity, PwC 2026)
        ssf_empr = gross * (flt(self.settings.ssf_employer_rate or 14.35) / 100) if gross > 0 else 0
        results["SSF Employer"] = {
            "amount": ssf_empr, "is_employer_only": True,
        }

        # 2. Solidarity Fund (1% employee)
        solidarity = gross * 0.01 if gross > 0 else 0
        results["Solidarity Fund"] = {
            "amount": solidarity, "is_employer_only": False,
        }

        # 3. PIT
        taxable = max(gross - ssf_emp - solidarity, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        # 4. Jehad Tax
        jehad = self._compute_jehad(gross)
        if jehad > 0:
            results["Jehad Tax"] = {
                "amount": jehad, "is_employer_only": False,
            }

        return results

    def _compute_pit(self, taxable_income):
        """PIT: 5% on first 12,000, 10% above."""
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 12000:
            return annual * 0.05 / 12
        return (12000 * 0.05 + (annual - 12000) * 0.10) / 12

    def _compute_jehad(self, gross):
        """Jehad Tax: 1-3% based on monthly income."""
        if gross <= 0:
            return 0
        if gross < 50:
            return gross * 0.01
        elif gross <= 100:
            return gross * 0.02
        else:
            return gross * 0.03
