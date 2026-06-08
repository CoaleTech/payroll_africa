"""Sao Tome and Principe statutory deduction calculator.

Reference: INSS Sao Tome and Principe
- INSS: Employer 8% (from Africa-HR reference)
- Employee contribution: minimal or 0%
- PIT: Progressive tax system
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class SaoTomePrincipeCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        ceiling = flt(self.settings.inss_ceiling or 500000)
        base = min(gross, ceiling) if gross > 0 else 0

        inss_emp = base * (flt(self.settings.inss_employee_rate or 3) / 100)
        inss_empr = base * (flt(self.settings.inss_employer_rate or 8) / 100)
        results["INSS Employee"] = {"amount": inss_emp, "is_employer_only": False}
        results["INSS Employer"] = {"amount": inss_empr, "is_employer_only": True}

        taxable = max(gross - inss_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        if annual <= 600000: return 0
        tax = 0
        for lower, upper, rate in [(600000, 1200000, 0.10), (1200000, 2400000, 0.15),
                                    (2400000, 0, 0.25)]:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
