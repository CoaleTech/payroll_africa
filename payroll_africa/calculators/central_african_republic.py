"""Central African Republic statutory deduction calculator.

Reference: CNSS CAR (limited data availability)
- CNSS: Employee ~3%, Employer ~14% (capped)
- Ceiling: cnss_ceiling field if non-zero; else 8x minimum wage
- PIT: Progressive tax system
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class CentralAfricanRepublicCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # Use cnss_ceiling if set; fall back to 8 × minimum_wage
        cnss_ceiling = getattr(self.settings, "cnss_ceiling", None)
        if cnss_ceiling:
            ceiling = flt(cnss_ceiling)
        else:
            min_wage = flt(getattr(self.settings, "minimum_wage", None) or 50000)
            ceiling = min_wage * 8
        base = min(gross, ceiling) if gross > 0 else 0

        cnss_emp = base * (flt(self.settings.cnss_employee_rate or 3) / 100)
        cnss_empr = base * (flt(self.settings.cnss_employer_rate or 14) / 100)
        results["CNSS Employee"] = {"amount": cnss_emp, "is_employer_only": False}
        results["CNSS Employer"] = {"amount": cnss_empr, "is_employer_only": True}

        taxable = max(gross - cnss_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        """PIT progressive (annual XAF bands).

        0 - 600,000     : 0%
        600,001 - 1,800,000: 10%
        1,800,001 - 3,600,000: 20%
        Over 3,600,000  : 30%

        Reads pit_bands from settings if populated; falls back to hardcoded.
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 600000:
            return 0

        bands = getattr(self.settings, "pit_bands", None) or []
        if bands:
            tax = 0
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if annual <= lower:
                    break
                band_top = upper if upper > 0 else annual
                amount = min(annual, band_top) - lower
                if amount > 0:
                    tax += amount * rate
            return tax / 12

        # Hardcoded fallback
        tax = 0
        for lower, upper, rate in [(600000, 1800000, 0.10), (1800000, 3600000, 0.20), (3600000, 0, 0.30)]:
            if annual <= lower:
                break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
