"""Mauritius statutory deduction calculator.

Reference: MRA (Mauritius Revenue Authority)
- PAYE (from July 2025): Simplified 3-band system
  First MUR 500,000: 0%, Next MUR 500,000: 10%, Remainder: 20%
  (Replaced 11-band system from Budget 2025-2026)
- NSF: Employee 1%, Employer 2.5% (capped at MUR 25,475/month)
- CSG: Employee 1.5%
- HRDC Levy: Employer 1.5%
- PRGF: Employer 2.5% (for qualifying employees)
- Exempt: < MUR 38,462/month
- Fair Share Contribution: 15% on income > MUR 12M (July 2025-June 2028)
- Tax year: July 1 - June 30
- PAYE is calculated on cumulative basis
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class MauritiusCalculator(BaseCalculator):
    """Mauritius statutory deduction calculator (2025/2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. NSF - Employee (1%, capped)
        nsf_employee = self._compute_nsf(gross)
        results["NSF Employee"] = {
            "amount": nsf_employee,
            "is_employer_only": False,
        }

        # NSF - Employer (2.5%, capped)
        nsf_employer = self._compute_nsf(gross, employer=True)
        results["NSF Employer"] = {
            "amount": nsf_employer,
            "is_employer_only": True,
        }

        # 2. CSG - Employee (tiered: 1.5% <= 50k, 3% > 50k)
        csg = self._compute_csg(gross)
        if csg > 0:
            results["CSG"] = {
                "amount": csg,
                "is_employer_only": False,
            }

        # 2b. CSG - Employer (tiered: 3% <= 50k, 6% > 50k)
        csg_empr = self._compute_csg_employer(gross)
        if csg_empr > 0:
            results["CSG Employer"] = {
                "amount": csg_empr,
                "is_employer_only": True,
            }

        # 3. HRDC Levy - Employer (1.5%)
        hrdc = self._compute_hrdc(gross)
        results["HRDC Levy"] = {
            "amount": hrdc,
            "is_employer_only": True,
        }

        # 4. PRGF - Employer (2.5%, for qualifying employees)
        prgf = self._compute_prgf(gross)
        if prgf > 0:
            results["PRGF"] = {
                "amount": prgf,
                "is_employer_only": True,
            }

        # 5. PAYE - progressive (simplified 3-band from July 2025)
        # Note: NSF is NOT deductible before PAYE in Mauritius
        paye = self._compute_paye(gross)
        if paye > 0:
            results["PAYE"] = {
                "amount": paye,
                "is_employer_only": False,
            }

        # 6. Fair Share Contribution (if applicable)
        fsc = self._compute_fair_share(gross)
        if fsc > 0:
            results["Fair Share Contribution"] = {
                "amount": fsc,
                "is_employer_only": False,
            }

        return results

    def _compute_nsf(self, gross, employer=False):
        """NSF: Employee 1%, Employer 2.5%, capped at MUR 25,475/month."""
        ceiling = flt(self.settings.nsf_ceiling or 28570)
        rate = flt(self.settings.nsf_employer_rate or 2.5) / 100 if employer else flt(self.settings.nsf_employee_rate or 1) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_csg(self, gross):
        """CSG Employee: 1.5% up to MUR 50,000/month, 3% above (PwC/MRA)."""
        if gross <= 0:
            return 0
        threshold = flt(self.settings.get("csg_high_threshold") or 50000)
        if gross <= threshold:
            rate = flt(self.settings.csg_rate or 1.5) / 100
        else:
            rate = flt(self.settings.get("csg_employee_high_rate") or 3) / 100
        return gross * rate

    def _compute_csg_employer(self, gross):
        """CSG Employer: 3% up to MUR 50,000/month, 6% above (PwC/MRA)."""
        if gross <= 0:
            return 0
        threshold = flt(self.settings.get("csg_high_threshold") or 50000)
        if gross <= threshold:
            rate = flt(self.settings.get("csg_employer_rate") or 3) / 100
        else:
            rate = flt(self.settings.get("csg_employer_high_rate") or 6) / 100
        return gross * rate

    def _compute_hrdc(self, gross):
        """HRDC Levy: 1.5% of gross (employer only, no cap)."""
        rate = flt(self.settings.hrdc_rate or 1.5) / 100
        return gross * rate if gross > 0 else 0

    def _compute_prgf(self, gross):
        """PRGF: 2.5% of gross (employer only, for qualifying employees)."""
        if not self.settings.get("prgf_applicable"):
            return 0
        rate = flt(self.settings.prgf_rate or 4.5) / 100
        # Exempt if basic > MUR 200,000/month
        basic = gross  # Use gross as proxy for basic pay
        if basic > flt(self.settings.prgf_exemption_threshold or 200000):
            return 0
        return gross * rate if gross > 0 else 0

    def _compute_paye(self, gross):
        """Compute PAYE using simplified 3-band system (from July 2025).

        Annual chargeable income bands (MUR):
        0 - 500,000        : 0%
        500,001 - 1,000,000: 10%
        Over 1,000,000     : 20%

        Exempt: monthly emoluments <= MUR 38,462
        """
        exempt_threshold = flt(self.settings.exempt_threshold_monthly or 38462)
        if gross <= exempt_threshold:
            return 0

        annual_income = gross * 12
        tax = 0

        # Simplified 3-band system (Budget 2025-2026)
        bands = self.settings.paye_bands or []
        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100
                if annual_income <= lower:
                    break
                band_top = upper if upper > 0 else annual_income
                taxable_in_band = min(annual_income, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            # Fallback simplified bands
            if annual_income <= 500000:
                tax = 0
            elif annual_income <= 1000000:
                tax = (annual_income - 500000) * 0.10
            else:
                tax = 500000 * 0.10 + (annual_income - 1000000) * 0.20

        return tax / 12

    def _compute_fair_share(self, gross):
        """Fair Share Contribution: 15% on income > MUR 12M/year.
        Applicable from July 2025 to June 2028.
        """
        if not self.settings.get("fair_share_applicable"):
            return 0
        annual_income = gross * 12
        threshold = flt(self.settings.fair_share_threshold or 12000000)
        rate = flt(self.settings.fair_share_rate or 15) / 100
        if annual_income <= threshold:
            return 0
        return (annual_income - threshold) * rate / 12
