"""South Africa statutory deduction calculator.

Reference: SARS (South African Revenue Service)
- PAYE: Progressive 18-45% (2024/2025 tax year, 1 March - 28/29 February)
- UIF: 2% total (1% employee + 1% employer), capped at R17,712/month
- SDL: 1% of total salary bill (employer only, if annual payroll > R500,000)
- ETI: Employment Tax Incentive (reduces PAYE for qualifying employees)
- Rebates: Primary R17,235, Secondary R9,444, Tertiary R3,145
- Tax thresholds: Under 65: R95,750; 65-74: R148,217; 75+: R165,689
"""

import frappe
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class SouthAfricaCalculator(BaseCalculator):
    """South Africa statutory deduction calculator (2024/2025 tax year)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. UIF Employee - 1% of gross, capped
        uif_employee = self._compute_uif(gross)
        results["UIF Employee"] = {
            "amount": uif_employee,
            "is_employer_only": False,
        }

        # UIF Employer - 1% of gross, capped (employer-only component)
        uif_employer = self._compute_uif(gross)
        results["UIF Employer"] = {
            "amount": uif_employer,
            "is_employer_only": True,
        }

        # 2. SDL - 1% of gross (employer only, if applicable)
        sdl = self._compute_sdl(gross)
        if sdl > 0:
            results["SDL"] = {
                "amount": sdl,
                "is_employer_only": True,
            }

        # 3. PAYE - progressive tax after rebates
        # Note: UIF is deductible before PAYE calculation
        taxable_income_annual = (gross - uif_employee) * 12
        paye_monthly = self._compute_paye(taxable_income_annual)
        results["PAYE"] = {
            "amount": paye_monthly,
            "is_employer_only": False,
        }

        return results

    def _compute_uif(self, gross):
        """UIF: 1% of gross salary, capped at R17,712/month."""
        ceiling = flt(self.settings.uif_ceiling or 17712)
        rate = flt(self.settings.uif_rate or 1) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_sdl(self, gross):
        """SDL: 1% of gross salary (employer only, if payroll > R500k/year)."""
        if not self.settings.get("sdl_applicable"):
            return 0
        rate = flt(self.settings.sdl_rate or 1) / 100
        return gross * rate if gross > 0 else 0

    def _compute_paye(self, taxable_annual):
        """Compute PAYE using SARS progressive annual bands (2024/2025).

        Annual taxable income bands (ZAR):
        0 - 237,100     : 18% of each R1 above threshold
        237,101 - 370,500: R42,678 + 26% above R237,100
        370,501 - 512,800: R77,362 + 31% above R370,500
        512,801 - 673,000: R121,475 + 36% above R512,800
        673,001 - 857,900: R179,147 + 39% above R673,000
        857,901 - 1,817,000: R251,258 + 41% above R857,900
        Over 1,817,000   : R644,489 + 45% above R1,817,000
        """
        if taxable_annual <= 0:
            return 0

        # Get age-based rebate and threshold
        age = self._get_employee_age()
        threshold, rebate = self._get_threshold_and_rebate(age)

        if taxable_annual <= threshold:
            return 0

        # Calculate tax using SARS formula method (more accurate)
        tax = self._sars_tax_formula(taxable_annual)

        # Subtract rebates
        tax = max(tax - rebate, 0)

        # Medical tax credits (if applicable)
        medical_credit = self._get_medical_tax_credit()
        tax = max(tax - medical_credit, 0)

        return tax / 12  # Monthly PAYE

    def _sars_tax_formula(self, annual_income):
        """SARS tax formula for 2024/2025 tax year."""
        bands = self.settings.paye_bands or []
        if bands:
            tax = 0
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
                    tax += base_tax
            return tax

        # Hardcoded fallback
        if annual_income <= 237100:
            return annual_income * 0.18
        elif annual_income <= 370500:
            return 42678 + (annual_income - 237100) * 0.26
        elif annual_income <= 512800:
            return 77362 + (annual_income - 370500) * 0.31
        elif annual_income <= 673000:
            return 121475 + (annual_income - 512800) * 0.36
        elif annual_income <= 857900:
            return 179147 + (annual_income - 673000) * 0.39
        elif annual_income <= 1817000:
            return 251258 + (annual_income - 857900) * 0.41
        else:
            return 644489 + (annual_income - 1817000) * 0.45

    def _get_threshold_and_rebate(self, age):
        """Get tax threshold and rebate based on age."""
        if age >= 75:
            threshold = flt(self.settings.threshold_75_plus or 165689)
            rebate = flt(self.settings.rebate_primary or 17235)
            rebate += flt(self.settings.rebate_secondary or 9444)
            rebate += flt(self.settings.rebate_tertiary or 3145)
        elif age >= 65:
            threshold = flt(self.settings.threshold_65_74 or 148217)
            rebate = flt(self.settings.rebate_primary or 17235)
            rebate += flt(self.settings.rebate_secondary or 9444)
        else:
            threshold = flt(self.settings.threshold_under_65 or 95750)
            rebate = flt(self.settings.rebate_primary or 17235)

        return threshold, rebate

    def _get_employee_age(self):
        """Get employee age from employee document."""
        try:
            dob = frappe.db.get_value("Employee", self.settings.get("employee"), "date_of_birth")
            if dob:
                from datetime import date
                today = date.today()
                return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except Exception:
            pass
        return 30  # Default assumption

    def _get_medical_tax_credit(self):
        """Get monthly medical tax credit."""
        # R332 for employee and first dependent, R224 for additional
        # This would typically come from employee settings
        credit = flt(self.settings.medical_tax_credit or 0)
        return credit * 12  # Annualize
