"""Ivory Coast (Cote d'Ivoire) statutory deduction calculator.

Reference: DGI (Direction Generale des Impots), CNPS
- ITS (Impôt sur les Traitements et Salaires): Progressive 0-32% (6 brackets)
  Replaced IS/CN/IGR via Ordinance 2023-718, effective Jan 1, 2024
- Standard deduction: 20% automatic on gross income (no cap)
- CNPS Retirement: Employee 6.3% + Employer 7.7% (capped at XOF 3,375,000/month)
- CNPS Family Allowances: Employer 5.75%
- CNPS Work Injury: Employer 2-5% (by risk)
- Vocational Training Tax: Employer 1.2%
- Housing Construction Fund: Employer 1.5%
- Tax credits: XOF 5,500 per half-share from 2nd bracket (max 5 shares)
"""

from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator


class IvoryCoastCalculator(BaseCalculator):
    """Ivory Coast statutory deduction calculator (2025/2026 rates)."""

    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}

        # 1. CNPS Retirement - Employee (6.3%, capped)
        cnps_employee = self._compute_cnps_employee(gross)
        results["CNPS Retirement Employee"] = {
            "amount": cnps_employee,
            "is_employer_only": False,
        }

        # CNPS Retirement - Employer (7.7%, capped)
        cnps_employer = self._compute_cnps_employer(gross)
        results["CNPS Retirement Employer"] = {
            "amount": cnps_employer,
            "is_employer_only": True,
        }

        # 2. CNPS Family Allowances - Employer only (5.75%)
        family_allow = self._compute_family_allowances(gross)
        results["CNPS Family Allowances"] = {
            "amount": family_allow,
            "is_employer_only": True,
        }

        # 3. Work Injury - Employer only (2-5% by risk class)
        work_injury = self._compute_work_injury(gross)
        if work_injury > 0:
            results["Work Injury Insurance"] = {
                "amount": work_injury,
                "is_employer_only": True,
            }

        # 4. Vocational Training Tax - Employer only (1.2%)
        training_tax = self._compute_training_tax(gross)
        results["Vocational Training Tax"] = {
            "amount": training_tax,
            "is_employer_only": True,
        }

        # 5. Housing Fund - Employer only (1.5%)
        housing_fund = self._compute_housing_fund(gross)
        results["Housing Construction Fund"] = {
            "amount": housing_fund,
            "is_employer_only": True,
        }

        # 6. ITS (Income Tax on Salaries) - progressive
        its = self._compute_its(gross)
        results["ITS"] = {
            "amount": its,
            "is_employer_only": False,
        }

        return results

    def _compute_cnps_employee(self, gross):
        """CNPS retirement employee: 6.3% of gross, capped."""
        ceiling = flt(self.settings.cnps_ceiling or 3375000)
        rate = flt(self.settings.cnps_employee_rate or 6.3) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_cnps_employer(self, gross):
        """CNPS retirement employer: 7.7% of gross, capped."""
        ceiling = flt(self.settings.cnps_ceiling or 3375000)
        rate = flt(self.settings.cnps_employer_rate or 7.7) / 100
        base = min(gross, ceiling) if gross > 0 else 0
        return base * rate

    def _compute_family_allowances(self, gross):
        """CNPS family allowances: 5.75% employer only."""
        rate = flt(self.settings.family_allowances_rate or 5.75) / 100
        return gross * rate if gross > 0 else 0

    def _compute_work_injury(self, gross):
        """Work injury insurance: 2-5% employer only, by risk class."""
        risk_class = flt(self.settings.work_injury_risk_class or 1)
        # Risk rates: Class 1 (office) = 2%, Class 2 = 2.5%, Class 3 = 3%, Class 4 = 4%, Class 5 = 5%
        risk_rates = {1: 2.0, 2: 2.5, 3: 3.0, 4: 4.0, 5: 5.0}
        rate = risk_rates.get(int(risk_class), 2.0) / 100
        return gross * rate if gross > 0 else 0

    def _compute_training_tax(self, gross):
        """Vocational training tax: 1.2% employer only."""
        rate = flt(self.settings.training_tax_rate or 1.2) / 100
        return gross * rate if gross > 0 else 0

    def _compute_housing_fund(self, gross):
        """Housing construction fund: 1.5% employer only."""
        rate = flt(self.settings.housing_fund_rate or 1.5) / 100
        return gross * rate if gross > 0 else 0

    def _compute_its(self, gross):
        """Compute ITS (Impôt sur les Traitements et Salaires).

        Steps:
        1. Apply 20% standard deduction to gross
        2. Apply progressive ITS brackets to net taxable
        3. Subtract tax credits (XOF 5,500 per half-share from 2nd bracket)

        Monthly ITS brackets (XOF):
        0 - 150,000      : 0%
        150,001 - 300,000: 12%
        300,001 - 500,000: 18%
        500,001 - 1,000,000: 25%
        1,000,001 - 2,000,000: 30%
        Over 2,000,000   : 32%
        """
        if gross <= 0:
            return 0

        # Step 1: 20% standard deduction
        standard_deduction_rate = flt(self.settings.standard_deduction_rate or 20) / 100
        taxable_income = gross * (1 - standard_deduction_rate)

        # Step 2: Progressive ITS
        tax = 0
        bands = self.settings.its_bands or []

        if bands:
            credit_threshold_band = 1  # From 2nd bracket onward
            for idx, band in enumerate(bands):
                lower = flt(band.from_amount)
                upper = flt(band.to_amount)
                rate = flt(band.rate) / 100

                if taxable_income <= lower:
                    break

                band_top = upper if upper > 0 else taxable_income
                taxable_in_band = min(taxable_income, band_top) - lower
                if taxable_in_band > 0:
                    tax += taxable_in_band * rate

            # Step 3: Tax credits
            tax = self._apply_tax_credits(tax, bands, taxable_income)
        else:
            tax = self._its_hardcoded(taxable_income)

        return max(tax, 0)

    def _its_hardcoded(self, taxable_income):
        """Hardcoded ITS calculation with tax credits."""
        tax = 0
        brackets = [
            (0, 150000, 0.00),
            (150000, 300000, 0.12),
            (300000, 500000, 0.18),
            (500000, 1000000, 0.25),
            (1000000, 2000000, 0.30),
            (2000000, 0, 0.32),
        ]

        credit_eligible = False
        for lower, upper, rate in brackets:
            if taxable_income <= lower:
                break
            if lower >= 150000:
                credit_eligible = True
            top = upper if upper > 0 else taxable_income
            amount = min(taxable_income, top) - lower
            if amount > 0:
                tax += amount * rate

        # Tax credits: XOF 5,500 per half-share from 2nd bracket
        if credit_eligible:
            num_shares = flt(self.settings.family_shares or 1)
            max_shares = flt(self.settings.max_shares or 5)
            credit_per_half_share = flt(self.settings.tax_credit_per_share or 5500)
            actual_shares = min(num_shares, max_shares)
            tax -= actual_shares * credit_per_half_share

        return max(tax, 0)

    def _apply_tax_credits(self, tax, bands, taxable_income):
        """Apply family tax credits."""
        # Credits apply from 2nd bracket onward
        second_bracket_lower = 0
        if len(bands) > 1:
            second_bracket_lower = flt(bands[1].from_amount)

        if taxable_income > second_bracket_lower and second_bracket_lower > 0:
            num_shares = flt(self.settings.family_shares or 1)
            max_shares = flt(self.settings.max_shares or 5)
            credit_per_half_share = flt(self.settings.tax_credit_per_share or 5500)
            actual_shares = min(num_shares, max_shares)
            tax -= actual_shares * credit_per_half_share

        return max(tax, 0)
