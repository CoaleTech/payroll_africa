"""Equatorial Guinea statutory deduction calculator.

Reference: CEMAC CNSS structure
- CNSS: Employer ~21.5%, Employee ~4.5% (capped)
- Includes: Pension, family allowances, work injury, health
- Ceiling: typically XAF 8x minimum wage
- PIT: Progressive tax system
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class EquatorialGuineaCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        min_wage = flt(self.settings.minimum_wage or 150000)
        ceiling = min_wage * 8
        base = min(gross, ceiling) if gross > 0 else 0

        cnss_emp = base * (flt(self.settings.cnss_employee_rate or 4.5) / 100)
        cnss_empr = base * (flt(self.settings.cnss_employer_rate or 21.5) / 100)
        results["CNSS Employee"] = {"amount": cnss_emp, "is_employer_only": False}
        results["CNSS Employer"] = {"amount": cnss_empr, "is_employer_only": True}

        # Work Protection Fund (WPF) — PwC 2025: employer 1%, employee 0.5%
        wpf_emp = base * (flt(self.settings.wpf_employee_rate or 0.5) / 100)
        wpf_empr = base * (flt(self.settings.wpf_employer_rate or 1) / 100)
        results["WPF Employee"] = {"amount": wpf_emp, "is_employer_only": False}
        results["WPF Employer"] = {"amount": wpf_empr, "is_employer_only": True}

        taxable = max(gross - cnss_emp - wpf_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        if annual <= 1000000: return 0
        tax = 0
        for lower, upper, rate in [(1000000, 3000000, 0.10), (3000000, 6000000, 0.15),
                                    (6000000, 10000000, 0.20), (10000000, 0, 0.25)]:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
