"""Guinea-Bissau statutory deduction calculator.

Reference: INSS Guinea-Bissau
- INSS: Employee 8%, Employer 14% (capped)
- PIT: Progressive 1-20% (9 bands)
- Annual threshold: XOF 500,000
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class GuineaBissauCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        min_wage = flt(self.settings.minimum_wage or 45000)
        ceiling = min_wage * 8
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
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        brackets = [(0, 500000, 0.01), (500000, 1000000, 0.06), (1000000, 2500000, 0.08),
                    (2500000, 3600000, 0.10), (3600000, 4806000, 0.12), (4806000, 9000000, 0.14),
                    (9000000, 13200000, 0.16), (13200000, 18000000, 0.18), (18000000, 0, 0.20)]
        tax = 0
        for lower, upper, rate in brackets:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
