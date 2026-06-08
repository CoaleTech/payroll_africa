"""Gambia statutory deduction calculator.

Reference: SSHFC (Social Security and Housing Finance Corporation)
- SSHFC: Employee 5%, Employer 10% (capped)
- PIT: Progressive 0-25%
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class GambiaCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        ceiling = flt(self.settings.sshfc_ceiling or 25000)
        base = min(gross, ceiling) if gross > 0 else 0

        sshfc_emp = base * (flt(self.settings.sshfc_employee_rate or 5) / 100)
        sshfc_empr = base * (flt(self.settings.sshfc_employer_rate or 10) / 100)
        results["SSHFC Employee"] = {"amount": sshfc_emp, "is_employer_only": False}
        results["SSHFC Employer"] = {"amount": sshfc_empr, "is_employer_only": True}

        taxable = max(gross - sshfc_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        if annual <= 18000: return 0
        tax = 0
        for lower, upper, rate in [(18000, 28000, 0.05), (28000, 38000, 0.10),
                                    (38000, 48000, 0.15), (48000, 58000, 0.20), (58000, 0, 0.25)]:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
