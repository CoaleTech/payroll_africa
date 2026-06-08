"""Mauritania statutory deduction calculator.

Reference: CNSS, CNAM, DGI
- CNSS: Employee 1%, Employer 15% (capped at MRU 15,000/month)
  Covers: Pension, family, work injury
- CNAM Health: Employee 4%, Employer 5%
- PIT (ITS): Progressive 0-40%
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class MauritaniaCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # CNSS
        cnss_ceiling = flt(self.settings.cnss_ceiling or 15000)
        cnss_base = min(gross, cnss_ceiling) if gross > 0 else 0
        cnss_emp = cnss_base * (flt(self.settings.cnss_employee_rate or 1) / 100)
        cnss_empr = cnss_base * (flt(self.settings.cnss_employer_rate or 15) / 100)
        results["CNSS Employee"] = {"amount": cnss_emp, "is_employer_only": False}
        results["CNSS Employer"] = {"amount": cnss_empr, "is_employer_only": True}

        # CNAM Health (uncapped)
        cnam_emp = gross * (flt(self.settings.cnam_employee_rate or 4) / 100) if gross > 0 else 0
        cnam_empr = gross * (flt(self.settings.cnam_employer_rate or 5) / 100) if gross > 0 else 0
        results["CNAM Health Employee"] = {"amount": cnam_emp, "is_employer_only": False}
        results["CNAM Health Employer"] = {"amount": cnam_empr, "is_employer_only": True}

        # PIT
        taxable = max(gross - cnss_emp - cnam_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        if annual <= 120000: return 0
        tax = 0
        for lower, upper, rate in [(120000, 360000, 0.15), (360000, 840000, 0.25),
                                    (840000, 1800000, 0.35), (1800000, 0, 0.40)]:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
