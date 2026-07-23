"""Eritrea statutory deduction calculator.

Reference: Eritrea has a closed economy with limited public payroll data.
The country operates a National Insurance Corporation of Eritrea (NICE)
and has income tax on employment income.
Data availability is very limited due to the closed nature of the economy.
This calculator implements the best available information.
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class EritreaCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # National insurance: ~6% employee, ~12% employer (estimated)
        nice_emp = gross * (flt(self.settings.nice_employee_rate or 6) / 100) if gross > 0 else 0
        nice_empr = gross * (flt(self.settings.nice_employer_rate or 6) / 100) if gross > 0 else 0
        results["NICE Employee"] = {"amount": nice_emp, "is_employer_only": False}
        results["NICE Employer"] = {"amount": nice_empr, "is_employer_only": True}

        # PIT: progressive (estimated based on available data)
        taxable = max(gross - nice_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        # Monthly PAYE bands (Inland Revenue / PAYE tables 2024-25)
        if taxable_income <= 0:
            return 0
        if taxable_income <= 800:
            return 0
        tax = 0
        for lower, upper, rate in [(800, 1000, 0.05), (1000, 1500, 0.10),
                                    (1500, 2000, 0.15), (2000, 3000, 0.20),
                                    (3000, 0, 0.30)]:
            if taxable_income <= lower:
                break
            amount = min(taxable_income, upper if upper > 0 else taxable_income) - lower
            if amount > 0:
                tax += amount * rate
        return tax
