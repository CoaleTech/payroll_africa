"""Morocco statutory deduction calculator.

Reference: DGI (Direction Generale des Impots), CNSS
- IR (Impôt sur le Revenu): Progressive 0-37% (6 brackets, 2026)
- CNSS Employee: 6.74% total
  - Pension/unemployment: 4.48% (capped at MAD 6,000/month)
  - AMO health: 2.26% (no cap)
- CNSS Employer: ~25.5% total
- Professional expense deduction: 20% of gross (capped at MAD 30,000/year)
- Annual tax exemption: MAD 40,000 (increased from 30,000 in 2025)
- Family allowance: MAD 500 per dependent (max MAD 3,000/year reduction)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class MoroccoCalculator(BaseCalculator):
    """Morocco statutory deduction calculator (2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNSS Employee contributions
        cnss_capped = self._compute_cnss_capped(gross)
        cnss_uncapped = self._compute_cnss_uncapped(gross)
        cnss_total_emp = cnss_capped + cnss_uncapped

        results["CNSS Employee"] = {
            "amount": cnss_total_emp,
            "is_employer_only": False,
        }

        # CNSS Employer contributions
        cnss_empr_capped = self._compute_cnss_employer_capped(gross)
        cnss_empr_uncapped = self._compute_cnss_employer_uncapped(gross)
        cnss_total_empr = cnss_empr_capped + cnss_empr_uncapped

        results["CNSS Employer"] = {
            "amount": cnss_total_empr,
            "is_employer_only": True,
        }

        # 2. IR (Income Tax) - progressive
        ir = self._compute_ir(gross, cnss_total_emp)
        results["IR"] = {
            "amount": ir,
            "is_employer_only": False,
        }

        return results

    def _compute_cnss_capped(self, gross):
        """CNSS pension/unemployment: 4.48% capped at MAD 6,000/month."""
        ceiling = flt(self.settings.cnss_ceiling or 6000)
        rate = flt(self.settings.cnss_capped_rate or 4.48) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_cnss_uncapped(self, gross):
        """CNSS AMO health: 2.26% uncapped."""
        rate = flt(self.settings.cnss_uncapped_rate or 2.26) / 100
        return gross * rate if gross > 0 else 0

    def _compute_cnss_employer_capped(self, gross):
        """Employer CNSS capped portion."""
        ceiling = flt(self.settings.cnss_ceiling or 6000)
        rate = flt(self.settings.cnss_employer_capped_rate or 8.6) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_cnss_employer_uncapped(self, gross):
        """Employer CNSS uncapped portion."""
        rate = flt(self.settings.cnss_employer_uncapped_rate or 4.11) / 100
        return gross * rate if gross > 0 else 0

    def _compute_ir(self, gross, cnss_total):
        """Compute IR (Impôt sur le Revenu).

        Steps:
        1. Deduct CNSS from gross
        2. Apply 20% professional expense deduction (capped at MAD 2,500/month)
        3. Subtract MAD 40,000 annual exemption
        4. Apply progressive rates
        5. Subtract family allowance (MAD 500 per dependent, max 6)
        """
        # Step 1: Deduct CNSS
        net_after_cnss = gross - cnss_total

        # Step 2: Professional expense deduction (20%, capped)
        prof_deduction_rate = flt(self.settings.professional_deduction_rate or 20) / 100
        prof_deduction_ceiling_monthly = flt(self.settings.professional_deduction_ceiling or 2500)
        prof_deduction = min(net_after_cnss * prof_deduction_rate, prof_deduction_ceiling_monthly)

        # Step 3: Annual exemption
        annual_exemption = flt(self.settings.annual_exemption or 40000)
        monthly_exemption = annual_exemption / 12

        # Taxable base
        taxable_monthly = max(net_after_cnss - prof_deduction - monthly_exemption, 0)
        taxable_annual = taxable_monthly * 12

        if taxable_annual <= 0:
            return 0

        # Step 4: Apply progressive rates
        tax_annual = self._apply_ir_bands(taxable_annual)

        # Step 5: Family allowance
        num_dependents = flt(self.settings.number_of_dependents or 0)
        max_dependents = flt(self.settings.max_dependents_for_allowance or 6)
        allowance_per_dependent = flt(self.settings.dependent_allowance or 500)
        actual_dependents = min(num_dependents, max_dependents)
        family_allowance = actual_dependents * allowance_per_dependent * 12

        tax_annual = max(tax_annual - family_allowance, 0)

        return tax_annual / 12

    def _apply_ir_bands(self, taxable_annual):
        """Apply IR progressive bands (2026 rates).

        Annual taxable income bands (MAD):
        0 - 40,000      : 0%
        40,001 - 60,000 : 10%
        60,001 - 80,000 : 20%
        80,001 - 100,000: 30%
        100,001 - 150,000: 34%
        Over 150,000    : 37%
        """
        tax = 0
        bands = self.settings.ir_bands or []

        if bands:
            for band in bands:
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100

                if taxable_annual <= lower:
                    break

                band_top = upper if upper > 0 else taxable_annual
                taxable_in_band = min(taxable_annual, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate
        else:
            tax = self._ir_hardcoded(taxable_annual)

        return tax

    def _ir_hardcoded(self, annual_income):
        """Hardcoded 2026 IR bands."""
        if annual_income <= 40000:
            return 0

        tax = 0
        brackets = [
            (40000, 60000, 0.10),
            (60000, 80000, 0.20),
            (80000, 100000, 0.30),
            (100000, 150000, 0.34),
            (150000, 0, 0.37),
        ]

        for lower, upper, rate in brackets:
            if annual_income <= lower:
                break
            top = upper if upper > 0 else annual_income
            amount = min(annual_income, top) - lower
            if amount > 0:
                tax += amount * rate

        return tax
