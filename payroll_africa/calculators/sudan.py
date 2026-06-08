"""Sudan statutory deduction calculator.

Reference: Sudan has a National Social Insurance Fund (NSIF)
but rates and structures are unclear due to ongoing conflict.
Some sources indicate: Employee ~8%, Employer ~17%
PIT: Progressive system with limited enforcement.
This calculator implements best available estimates.
Note: Data reliability is low due to conflict situation.
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class SudanCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        ceiling = flt(self.settings.nsif_ceiling or 100000)
        base = min(gross, ceiling) if gross > 0 else 0

        nsif_emp = base * (flt(self.settings.nsif_employee_rate or 8) / 100)
        nsif_empr = base * (flt(self.settings.nsif_employer_rate or 17) / 100)
        results["NSIF Employee"] = {"amount": nsif_emp, "is_employer_only": False}
        results["NSIF Employer"] = {"amount": nsif_empr, "is_employer_only": True}

        taxable = max(gross - nsif_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        if annual <= 120000: return 0
        tax = 0
        for lower, upper, rate in [(120000, 360000, 0.10), (360000, 720000, 0.15),
                                    (720000, 0, 0.20)]:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
