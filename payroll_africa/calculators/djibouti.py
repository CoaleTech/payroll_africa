"""Djibouti statutory deduction calculator.

Reference: CNSS Djibouti (limited data)
- CNSS: Employee ~4%, Employer ~12% (capped)
- PIT: Progressive 0-30%
- Limited formal employment sector
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class DjiboutiCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        ceiling = flt(self.settings.cnss_ceiling or 400000)
        base = min(gross, ceiling) if gross > 0 else 0

        cnss_emp = base * (flt(self.settings.cnss_employee_rate or 2) / 100)
        cnss_empr = base * (flt(self.settings.cnss_employer_rate or 5) / 100)
        results["CNSS Employee"] = {"amount": cnss_emp, "is_employer_only": False}
        results["CNSS Employer"] = {"amount": cnss_empr, "is_employer_only": True}

        taxable = max(gross - cnss_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        if annual <= 240000: return 0
        tax = 0
        for lower, upper, rate in [(240000, 600000, 0.10), (600000, 1200000, 0.20),
                                    (1200000, 0, 0.30)]:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
