"""Cabo Verde statutory deduction calculator.

Reference: INPS Cabo Verde
- INPS: Employee 8.5%, Employer 16%
  Covers: Pension, sickness, maternity, family, unemployment, work accident
- Work injury insurance: Employer 2-6% by risk (separate from INPS)
- PIT (IRPS): Progressive 0-27.5%
  Annual threshold: ~CVE 300,000
- Ceiling: CVE 80,000/month
- 13th month: Common practice but not mandatory
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class CaboVerdeCalculator(BaseCalculator):
    def compute(self, salary_slip):
        gross = self.get_gross_pay(salary_slip)
        results = {}
        ceiling = flt(self.settings.inps_ceiling or 80000)
        base = min(gross, ceiling) if gross > 0 else 0

        inps_emp = base * (flt(self.settings.inps_employee_rate or 8.5) / 100)
        inps_empr = base * (flt(self.settings.inps_employer_rate or 16) / 100)
        results["INPS Employee"] = {"amount": inps_emp, "is_employer_only": False}
        results["INPS Employer"] = {"amount": inps_empr, "is_employer_only": True}

        # Work injury (separate insurance)
        risk = flt(self.settings.work_injury_risk or 1)
        rates = {1: 2.0, 2: 4.0, 3: 6.0}
        injury = gross * (rates.get(int(risk), 2.0) / 100) if gross > 0 else 0
        results["Work Injury Insurance"] = {"amount": injury, "is_employer_only": True}

        taxable = max(gross - inps_emp, 0)
        pit = self._compute_pit(taxable)
        if pit > 0:
            results["PIT"] = {"amount": pit, "is_employer_only": False}
        return results

    def _compute_pit(self, taxable_income):
        if taxable_income <= 0: return 0
        annual = taxable_income * 12
        if annual <= 220000: return 0
        tax = 0
        for lower, upper, rate in [(220000, 960000, 0.165), (960000, 1800000, 0.231),
                                    (1800000, 0, 0.275)]:
            if annual <= lower: break
            amount = min(annual, upper if upper > 0 else annual) - lower
            if amount > 0: tax += amount * rate
        return tax / 12
