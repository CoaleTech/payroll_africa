"""Namibia statutory deduction calculator.

Reference: Namibia Revenue Agency (NamRA), SSC
- PAYE: Progressive 0-37% (2025/26 NamRA schedule)
- Social Security (SSC): 0.9% employee + 0.9% employer (capped at NAD 150,000/year from Sep 2026)
- VET Levy: 1% of gross payroll (employer only, if annual payroll > NAD 1M)
- Employees' Compensation Fund (ECF): Employer <1-8% by risk sector

Sources: Deloitte Namibia tax alert 25 Aug 2026; Sage Namibia statutory update Aug 2026;
         PwC Worldwide Tax Summaries Namibia (reviewed Jul 2026); countrytaxcalc.com
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
        """SSC: 0.9% of gross, capped at NAD 150,000/year (N$12,500/month, from 1 Sep 2026)."""
        ceiling_annual = flt(self.settings.ssc_annual_ceiling or 150000)
        ceiling_monthly = ceiling_annual / 12
        rate = self._num("ssc_rate", 0.9) / 100
        base = min(gross, ceiling_monthly) if gross > 0 else 0
        return base * rate

    def _compute_vet_levy(self, gross):
        """VET Levy: 1% of gross (employer only, if payroll > NAD 1M/year)."""
        if not self.settings.get("vet_levy_applicable"):
            return 0
        rate = self._num("vet_levy_rate", 1) / 100
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
        """Compute PAYE using progressive annual bands (2025/26 NamRA schedule).

        Each band carries a ``base_tax`` representing cumulative tax at the
        bottom of that band.  We find the single matching band and return
        ``base_tax + (income − lower) × rate`` divided by 12 for monthly.

        Annual taxable income bands (NAD, PwC/NamRA 2025/26):
        0 - 100,000          : 0 %
        100,001 - 150,000    : 18 % above 100,000
        150,001 - 350,000    : 9,000 + 25 % above 150,000
        350,001 - 550,000    : 59,000 + 28 % above 350,000
        550,001 - 850,000    : 115,000 + 30 % above 550,000
        850,001 - 1,550,000  : 205,000 + 32 % above 850,000
        Over 1,550,000       : 429,000 + 37 % above 1,550,000
        """
        if gross <= 0:
            return 0

        annual_income = gross * 12

        bands = self.settings.paye_bands or []
        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                base_tax = flt(band.base_tax or 0)
                rate = flt(band.rate) / 100

                if annual_income <= lower:
                    break

                band_top = upper if upper > 0 else float("inf")
                if annual_income <= band_top:
                    # Matching band found — return its contribution only
                    return (base_tax + (annual_income - lower) * rate) / 12

            return 0  # income below first band's lower (shouldn't happen)

        return self._paye_hardcoded(annual_income) / 12

    def _paye_hardcoded(self, annual_income):
        """Hardcoded PAYE fallback (2025/26 NamRA bands)."""
        if annual_income <= 100000:
            return 0
        elif annual_income <= 150000:
            return (annual_income - 100000) * 0.18
        elif annual_income <= 350000:
            return 9000 + (annual_income - 150000) * 0.25
        elif annual_income <= 550000:
            return 59000 + (annual_income - 350000) * 0.28
        elif annual_income <= 850000:
            return 115000 + (annual_income - 550000) * 0.30
        elif annual_income <= 1550000:
            return 205000 + (annual_income - 850000) * 0.32
        else:
            return 429000 + (annual_income - 1550000) * 0.37
