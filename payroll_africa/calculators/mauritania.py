"""Mauritania statutory deduction calculator.

Reference: CNSS, CNAM, DGI
- CNSS: Employee 1%, Employer 15% (capped at MRU 15,000/month)
  Covers: Pension, family, work injury
- CNAM Health: Employee 4%, Employer 5% (uncapped)
- PIT (ITS): Progressive 0-40%
  Annual threshold: MRU 72,000
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class MauritaniaCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # CNSS (capped)
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
        """ITS progressive.

        Annual bands (MRU):
        0 - 72,000        : 0%
        72,001 - 108,000  : 15%
        108,001 - 252,000 : 25%
        Over 252,000      : 40%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        # Read bands from settings if populated; fall back to hardcoded statutory rates.
        bands = getattr(self.settings, "pit_bands", None) or []
        if bands:
            return self._compute_tax_from_bands(annual, bands) / 12

        if annual <= 72000:
            return 0
        tax = 0
        for lower, upper, rate in [
            (72000, 108000, 0.15),
            (108000, 252000, 0.25),
            (252000, 0, 0.40),
        ]:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
