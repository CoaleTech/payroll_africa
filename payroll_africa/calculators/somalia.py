"""Somalia statutory deduction calculator.

Reference: Somalia has no mandatory national social security system.
Some private schemes exist but are not statutory.
PIT: Limited formal income tax system. Tax-free zone in practice for most.
This calculator returns empty results - the country has no statutory payroll deductions.
Note: Users should configure custom deductions if private schemes apply.
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class SomaliaCalculator(BaseCalculator):
    def compute(self, salary_slip):
        # Somalia has no mandatory statutory payroll deductions
        return {}
