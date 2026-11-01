"""Algeria statutory deduction calculator.

Reference: CNAS, DGI
- CNAS Social Security: Employee 9%, Employer 26%
  (Health, maternity, work injury, pension, family allowances)
- PIT (IRG): Progressive 0-35% (6 brackets)
  Annual: 0-240k@0%, 240k-480k@23%, 480k-960k@27%, 960k-1920k@30%, 1920k-3840k@33%, 3840k+@35%
- Tax year: January 1 - December 31
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

_HARDCODED_PIT_BRACKETS = [
    (240000, 480000, 0.23),
    (480000, 960000, 0.27),
    (960000, 1920000, 0.30),
    (1920000, 3840000, 0.33),
    (3840000, 0, 0.35),
]


class AlgeriaCalculator(BaseCalculator):
    """Algeria statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNAS Employee (9%)
        emp_rate = self.settings.cnas_employee_rate
        cnas_emp = gross * (flt(emp_rate if emp_rate is not None else 9) / 100) if gross > 0 else 0
        results["CNAS Employee"] = {
            "amount": cnas_emp, "is_employer_only": False,
        }

        # CNAS Employer (26%)
        empr_rate = self.settings.cnas_employer_rate
        cnas_empr = gross * (flt(empr_rate if empr_rate is not None else 26) / 100) if gross > 0 else 0
        results["CNAS Employer"] = {
            "amount": cnas_empr, "is_employer_only": True,
        }

        # 2. PIT (IRG)
        taxable = max(gross - cnas_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        return results

    def _compute_pit(self, taxable_income):
        """PIT progressive annual bands.

        Reads from settings.pit_bands if populated; falls back to hardcoded 2025 brackets.

        Annual bands (DZD):
        0 - 240,000        : 0%
        240,001 - 480,000  : 23%
        480,001 - 960,000  : 27%
        960,001 - 1,920,000: 30%
        1,920,001 - 3,840,000: 33%
        Over 3,840,000     : 35%
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
        if annual <= 240000:
            return 0
        tax = 0
        for lower, upper, rate in _HARDCODED_PIT_BRACKETS:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
