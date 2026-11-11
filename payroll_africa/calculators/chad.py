"""Chad statutory deduction calculator.

Reference: CNPS Chad (PwC 2024, Central Africa Tax Guide 2023)
- CNPS Pension: Employee 3.5%, Employer 5%
- CNPS Family Allowances: Employer 7.5%
- CNPS Work Injury: Employer 2-5% by risk
- PIT: Progressive 0-30%
- Ceiling: cnps_ceiling field if non-zero, else 8x minimum wage (legal ceiling 500,000 XAF/month)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class ChadCalculator(BaseCalculator):
    """Chad statutory deduction calculator."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        base = self._get_contribution_base(gross)

        # 1. CNPS Pension
        pension_emp = base * (self._num("cnps_pension_employee_rate", 3.5) / 100)
        pension_empr = base * (self._num("cnps_pension_employer_rate", 5) / 100)
        results["CNPS Pension Employee"] = {
            "amount": pension_emp, "is_employer_only": False,
        }
        results["CNPS Pension Employer"] = {
            "amount": pension_empr, "is_employer_only": True,
        }

        # 2. CNPS Family Allowances - Employer only (field: family_allowances_rate)
        fam_rate = getattr(self.settings, "family_allowances_rate", None)
        family = base * (flt(fam_rate if fam_rate is not None else 7.5) / 100)
        results["CNPS Family Allowances"] = {
            "amount": family, "is_employer_only": True,
        }

        # 3. Work Injury - Employer only
        risk_class = flt(self.settings.work_injury_risk_class or 1)
        risk_rates = {1: 2.0, 2: 3.0, 3: 5.0}
        injury = gross * (risk_rates.get(int(risk_class), 2.0) / 100) if gross > 0 else 0
        results["Work Injury Insurance"] = {
            "amount": injury, "is_employer_only": True,
        }

        # 4. PIT
        taxable = max(gross - pension_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {
                "amount": pit, "is_employer_only": False,
            }

        return results

    def _get_contribution_base(self, gross):
        cnps_ceiling = getattr(self.settings, "cnps_ceiling", None)
        if cnps_ceiling:
            ceiling = flt(cnps_ceiling)
        else:
            min_wage = flt(getattr(self.settings, "minimum_wage", None) or 60000)
            ceiling = min_wage * 8
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_pit(self, taxable_income):
        """PIT progressive (annual XAF bands matching seeded pit_bands table).

        Reads pit_bands from settings if populated; falls back to hardcoded bands:
          0 - 800,000       : 0%
          800,001 - 6,000,000: 10.5%
          6,000,001 - 7,500,000: 15%
          7,500,001 - 9,000,000: 20%
          9,000,001 - 12,000,000: 25%
          Over 12,000,000   : 30%
        """
        if taxable_income <= 0:
            return 0
        annual = taxable_income * 12
        if annual <= 800000:
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

        # Hardcoded fallback (matches seeded bands)
        tax = 0
        brackets = [
            (800000, 6000000, 0.105),
            (6000000, 7500000, 0.15),
            (7500000, 9000000, 0.20),
            (9000000, 12000000, 0.25),
            (12000000, 0, 0.30),
        ]
        for lower, upper, rate in brackets:
            if annual <= lower:
                break
            top = upper if upper > 0 else annual
            amount = min(annual, top) - lower
            if amount > 0:
                tax += amount * rate
        return tax / 12
