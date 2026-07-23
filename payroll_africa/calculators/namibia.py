"""Namibia statutory deduction calculator.

Reference: Namibia Revenue Agency (NamRA), SSC
- PAYE: Progressive 0-37%
- Social Security (SSC): 0.9% employee + 0.9% employer (capped at NAD 108,000/year)
- VET Levy: 1% of gross payroll (employer only, if annual payroll > NAD 1M)
- Employees' Compensation Fund (ECF): Employer <1-8% by risk sector
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class NamibiaCalculator(BaseCalculator):
    """Namibia statutory deduction calculator (2025/2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. Social Security - Employee (0.9%, capped)
        ssc_employee = self._compute_ssc(gross)
        results["Social Security Employee"] = {
            "amount": ssc_employee,
            "is_employer_only": False,
        }

        # Social Security - Employer (0.9%, capped)
        ssc_employer = self._compute_ssc(gross)
        results["Social Security Employer"] = {
            "amount": ssc_employer,
            "is_employer_only": True,
        }

        # 2. VET Levy - Employer only (1%, if applicable)
        vet_levy = self._compute_vet_levy(gross)
        if vet_levy > 0:
            results["VET Levy"] = {
                "amount": vet_levy,
                "is_employer_only": True,
            }

        # 3. ECF - Employer only (by risk sector)
        ecf = self._compute_ecf(gross)
        if ecf > 0:
            results["Employees Compensation"] = {
                "amount": ecf,
                "is_employer_only": True,
            }

        # 4. PAYE - progressive
        paye = self._compute_paye(gross)
        results["PAYE"] = {
            "amount": paye,
            "is_employer_only": False,
        }

        return results

    def _compute_ssc(self, gross):
        """SSC: 0.9% of gross, capped at NAD 108,000/year (NAD 9,000/month)."""
        ceiling_annual = flt(self.settings.ssc_annual_ceiling or 132000)   # SSC GN 8461, Mar 2025
        ceiling_monthly = ceiling_annual / 12
        rate = flt(self.settings.ssc_rate or 0.9) / 100
        base = min(gross, ceiling_monthly) if gross > 0 else 0
        return base * rate

    def _compute_vet_levy(self, gross):
        """VET Levy: 1% of gross (employer only, if payroll > NAD 1M/year)."""
        if not self.settings.get("vet_levy_applicable"):
            return 0
        rate = flt(self.settings.vet_levy_rate or 1) / 100
        return gross * rate if gross > 0 else 0

    def _compute_ecf(self, gross):
        """Employees Compensation Fund: <1-8% by risk sector (employer only)."""
        risk_sector = self.settings.get("ecf_risk_sector", "low")
        risk_rates = {
            "low": 1.0,
            "medium": 3.0,
            "high": 5.0,
            "very_high": 8.0,
        }
        rate = risk_rates.get(risk_sector, 1.0) / 100
        return gross * rate if gross > 0 else 0

    def _compute_paye(self, gross):
        """Compute PAYE using progressive annual bands.

        Annual taxable income bands (NAD):
        0 - 100,000       : 0%
        100,001 - 250,000 : 18% above 100,000
        250,001 - 500,000 : 27,000 + 25% above 250,000
        500,001 - 750,000 : 89,500 + 28% above 500,000
        750,001 - 1,000,000: 159,500 + 30% above 750,000
        1,000,001 - 1,500,000: 234,500 + 32% above 1,000,000
        Over 1,500,000    : 394,500 + 37% above 1,500,000
        """
        if gross <= 0:
            return 0

        annual_income = gross * 12
        tax = 0

        bands = self.settings.paye_bands or []
        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                base_tax = flt(band.base_tax or 0)
                rate = flt(band.rate) / 100

                if annual_income <= lower:
                    break

                band_top = upper if upper > 0 else annual_income
                taxable_in_band = min(annual_income, band_top) - lower
                if taxable_in_band > 0:
                    tax += base_tax + taxable_in_band * rate
        else:
            tax = self._paye_hardcoded(annual_income)

        return tax / 12

    def _paye_hardcoded(self, annual_income):
        """Hardcoded PAYE formula."""
        if annual_income <= 100000:
            return 0
        elif annual_income <= 250000:
            return (annual_income - 100000) * 0.18
        elif annual_income <= 500000:
            return 27000 + (annual_income - 250000) * 0.25
        elif annual_income <= 750000:
            return 89500 + (annual_income - 500000) * 0.28
        elif annual_income <= 1000000:
            return 159500 + (annual_income - 750000) * 0.30
        elif annual_income <= 1500000:
            return 234500 + (annual_income - 1000000) * 0.32
        else:
            return 394500 + (annual_income - 1500000) * 0.37
