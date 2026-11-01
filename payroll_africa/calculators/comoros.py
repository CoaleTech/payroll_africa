"""Comoros statutory deduction calculator.

Reference: Caisse Nationale de Securite Sociale (CNSS) Comoros
- CNSS: Employee 3.5%, Employer 10.5% (capped at KMF 8x minimum wage)
- PIT: Progressive 0-30%; reads from settings.pit_bands if populated
- Tax year: January 1 - December 31
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

_HARDCODED_PIT_BRACKETS = [
    (360000, 720000, 0.10),
    (720000, 1440000, 0.15),
    (1440000, 2880000, 0.20),
    (2880000, 0, 0.30),
]


class ComorosCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        min_wage_val = getattr(self.settings, 'minimum_wage', None)
        min_wage = flt(min_wage_val if min_wage_val is not None else 55000)
        ceiling = min_wage * 8
        base = min(gross, ceiling) if gross > 0 else 0

        cnss_emp_rate = self.settings.cnss_employee_rate
        cnss_empr_rate = self.settings.cnss_employer_rate
        cnss_emp = base * (flt(cnss_emp_rate if cnss_emp_rate is not None else 3.5) / 100)
        cnss_empr = base * (flt(cnss_empr_rate if cnss_empr_rate is not None else 10.5) / 100)
        results["CNSS Employee"] = {"amount": cnss_emp, "is_employer_only": False}
        results["CNSS Employer"] = {"amount": cnss_empr, "is_employer_only": True}

        taxable = max(gross - cnss_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        """PIT progressive bands.

        Reads from settings.pit_bands if populated; falls back to hardcoded 2025 brackets.
        Uses settings.pit_threshold as the zero-rate floor (default 360,000 KMF/year).

        Annual bands (KMF):
        0 - 360,000   : 0%
        360,001 - 720,000  : 10%
        720,001 - 1,440,000: 15%
        1,440,001 - 2,880,000: 20%
        2,880,001+    : 30%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12

        bands = getattr(self.settings, 'pit_bands', None)
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if annual <= lower:
                    break
                top = upper if upper > 0 else annual
                amount = min(annual, top) - lower
                if amount > 0:
                    tax += amount * rate
            return tax / 12

        # Hardcoded fallback
        pit_threshold = getattr(self.settings, 'pit_threshold', None)
        threshold = flt(pit_threshold if pit_threshold is not None else 360000)
        if annual <= threshold:
            return 0
        tax = 0
        for lower, upper, rate in _HARDCODED_PIT_BRACKETS:
            if annual <= lower:
                break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
