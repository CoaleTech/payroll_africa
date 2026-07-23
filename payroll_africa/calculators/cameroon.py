"""Cameroon statutory deduction calculator.

Reference: DGI, CNPS
- CNPS Pension: Employee 4.2%, Employer 4.2% (capped at XAF 750,000/month)
- CNPS Family Allowances: Employer 7% (capped)
- Work Injury: Employer 1.75%/2.5%/5% by risk (uncapped)
- CFC (Housing Fund): Employee 1%, Employer 1.5%
- FNE (Employment Fund): Employer 1%
- PIT (IRPP): Progressive 10%/15%/25%/35% + 10% CAC surcharge
  Effective rates: 11%/16.5%/27.5%/38.5%
- Deductions: CNPS 4.2%, 30% professional abatement, XAF 500,000 standard
- PIT exemption: < XAF 62,000/month
- CRTV (Audiovisual): Banded, max XAF 13,000
- Taxe Communale: Banded, max XAF 2,520
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class CameroonCalculator(BaseCalculator):
    """Cameroon statutory deduction calculator (2025 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNPS Pension - Employee (4.2%, capped)
        cnps_pension_emp = self._compute_cnps_pension_employee(gross)
        results["CNPS Pension Employee"] = {
            "amount": cnps_pension_emp,
            "is_employer_only": False,
        }

        # CNPS Pension - Employer (4.2%, capped)
        cnps_pension_empr = self._compute_cnps_pension_employer(gross)
        results["CNPS Pension Employer"] = {
            "amount": cnps_pension_empr,
            "is_employer_only": True,
        }

        # 2. CNPS Family Allowances - Employer only (7%, capped)
        family_allow = self._compute_family_allowances(gross)
        results["CNPS Family Allowances"] = {
            "amount": family_allow,
            "is_employer_only": True,
        }

        # 3. Work Injury - Employer only (by risk class)
        work_injury = self._compute_work_injury(gross)
        results["Work Injury Insurance"] = {
            "amount": work_injury,
            "is_employer_only": True,
        }

        # 4. CFC (Housing Fund)
        cfc_employee = self._compute_cfc_employee(gross)
        cfc_employer = self._compute_cfc_employer(gross)
        results["CFC Housing Employee"] = {
            "amount": cfc_employee,
            "is_employer_only": False,
        }
        results["CFC Housing Employer"] = {
            "amount": cfc_employer,
            "is_employer_only": True,
        }

        # 5. FNE (Employment Fund) - Employer only (1%)
        fne = self._compute_fne(gross)
        results["FNE Employment Fund"] = {
            "amount": fne,
            "is_employer_only": True,
        }

        # 6. PIT (IRPP) - progressive (if above exemption)
        pit = self._compute_pit(gross, cnps_pension_emp)
        if pit > 0:
            results["PIT"] = {
                "amount": pit,
                "is_employer_only": False,
            }

        # 7. CRTV (Audiovisual royalty) - if gross > 1,000,000
        crtv = self._compute_crtv(gross)
        if crtv > 0:
            results["CRTV Royalty"] = {
                "amount": crtv,
                "is_employer_only": False,
            }

        # 8. Taxe Communale (local tax) - if gross > 500,000
        taxe_com = self._compute_taxe_communale(gross)
        if taxe_com > 0:
            results["Taxe Communale"] = {
                "amount": taxe_com,
                "is_employer_only": False,
            }

        return results

    def _get_cnps_base(self, gross):
        """Get CNPS contribution base capped at XAF 750,000."""
        ceiling = flt(self.settings.cnps_ceiling or 750000)
        return min(gross, ceiling) if gross > 0 else 0

    def _compute_cnps_pension_employee(self, gross):
        """CNPS pension employee: 4.2% of capped base."""
        rate = flt(self.settings.cnps_pension_employee_rate or 4.2) / 100
        base = self._get_cnps_base(gross)
        return base * rate

    def _compute_cnps_pension_employer(self, gross):
        """CNPS pension employer: 4.2% of capped base."""
        rate = flt(self.settings.cnps_pension_employer_rate or 4.2) / 100
        base = self._get_cnps_base(gross)
        return base * rate

    def _compute_family_allowances(self, gross):
        """CNPS family allowances: 7% employer only, capped."""
        rate = flt(self.settings.family_allowances_rate or 7) / 100
        base = self._get_cnps_base(gross)
        return base * rate

    def _compute_work_injury(self, gross):
        """Work injury: 1.75%/2.5%/5% employer only by risk."""
        risk_class = flt(self.settings.work_injury_risk_class or 1)
        risk_rates = {1: 1.75, 2: 2.5, 3: 5.0}
        rate = risk_rates.get(int(risk_class), 1.75) / 100
        return gross * rate if gross > 0 else 0

    def _compute_cfc_employee(self, gross):
        """CFC housing fund employee: 1%."""
        rate = flt(self.settings.cfc_employee_rate or 1) / 100
        return gross * rate if gross > 0 else 0

    def _compute_cfc_employer(self, gross):
        """CFC housing fund employer: 1.5%."""
        rate = flt(self.settings.cfc_employer_rate or 1.5) / 100
        return gross * rate if gross > 0 else 0

    def _compute_fne(self, gross):
        """FNE employment fund: 1% employer only."""
        rate = flt(self.settings.fne_rate or 1) / 100
        return gross * rate if gross > 0 else 0

    def _compute_pit(self, gross, cnps_employee):
        """Compute PIT (IRPP) using progressive annual bands.

        Steps:
        1. Annual gross
        2. Less CNPS employee (4.2%)
        3. Less 30% professional expense abatement
        4. Less XAF 500,000 standard deduction
        5. Round down to nearest 1,000
        6. Apply progressive rates + 10% CAC surcharge
        """
        exemption_monthly = flt(self.settings.pit_exemption_monthly or 62000)
        if gross < exemption_monthly:
            return 0

        annual_gross = gross * 12

        # Step 1: Less CNPS
        annual_cnps = cnps_employee * 12

        # Step 2: 30% professional abatement applied to (gross - CNPS), per DGI formula
        prof_abatement = flt(self.settings.professional_abatement_rate or 30) / 100
        net_of_cnps = annual_gross - annual_cnps
        prof_deduction = net_of_cnps * prof_abatement

        # Step 3: Standard deduction
        standard_deduction = flt(self.settings.standard_deduction or 500000)

        taxable_annual = max(net_of_cnps - prof_deduction - standard_deduction, 0)

        # Round down to nearest 1,000
        taxable_annual = (taxable_annual // 1000) * 1000

        if taxable_annual <= 0:
            return 0

        # Apply progressive rates
        tax = self._apply_pit_bands(taxable_annual)

        return tax / 12

    def _apply_pit_bands(self, taxable_annual):
        """Apply PIT progressive bands with CAC surcharge.

        Annual bands (XAF):
        0 - 2,000,000     : 10% base (11% effective with CAC)
        2,000,001 - 3,000,000 : 15% (16.5% effective)
        3,000,001 - 5,000,000 : 25% (27.5% effective)
        Over 5,000,000    : 35% (38.5% effective)
        """
        cac_rate = 1 + (flt(self.settings.cac_surcharge_rate or 10) / 100)
        tax = 0

        bands = self.settings.pit_bands or []
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
                    tax += taxable_in_band * rate * cac_rate
        else:
            tax = self._pit_hardcoded(taxable_annual, cac_rate)

        return tax

    def _pit_hardcoded(self, taxable_annual, cac_rate):
        """Hardcoded PIT with CAC surcharge."""
        if taxable_annual <= 0:
            return 0

        tax = 0
        brackets = [
            (0, 2000000, 0.10),
            (2000000, 3000000, 0.15),
            (3000000, 5000000, 0.25),
            (5000000, 10000000, 0.35),
            (10000000, 0, 0.385),
        ]

        for lower, upper, rate in brackets:
            if taxable_annual <= lower:
                break
            top = upper if upper > 0 else taxable_annual
            amount = min(taxable_annual, top) - lower
            if amount > 0:
                tax += amount * rate * cac_rate

        return tax

    def _compute_crtv(self, gross):
        """CRTV audiovisual royalty: banded, max XAF 13,000."""
        if gross <= 1000000:
            return 0
        bands = self.settings.crtv_bands or []
        if bands:
            for band in bands:
                if gross <= flt(band.to_amount):
                    return flt(band.amount)
        # Hardcoded fallback
        if gross <= 1200000:
            return 500
        elif gross <= 1500000:
            return 1000
        elif gross <= 2000000:
            return 2000
        elif gross <= 3000000:
            return 3000
        elif gross <= 5000000:
            return 5000
        elif gross <= 7000000:
            return 7000
        elif gross <= 10000000:
            return 10000
        else:
            return 13000

    def _compute_taxe_communale(self, gross):
        """Taxe communale: banded, max XAF 2,520."""
        if gross <= 500000:
            return 0
        max_taxe = flt(self.settings.taxe_communale_max or 2520)
        bands = self.settings.taxe_communale_bands or []
        if bands:
            for band in bands:
                if gross <= flt(band.to_amount):
                    return flt(band.amount)
        # Hardcoded fallback
        if gross <= 600000:
            return 500
        elif gross <= 800000:
            return 1000
        elif gross <= 1000000:
            return 1500
        elif gross <= 1500000:
            return 2000
        else:
            return max_taxe
