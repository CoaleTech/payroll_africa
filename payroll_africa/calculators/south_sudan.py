"""South Sudan statutory deduction calculator.

Reference: Very limited formal payroll framework.
No mandatory national social security system exists.
Some employers may have private pension/insurance schemes.
Tax system is evolving and varies by sector.
"""
from frappe.utils import flt
from payroll_africa.calculators.base import BaseCalculator

class SouthSudanCalculator(BaseCalculator):
    def compute(self, salary_slip):
        # South Sudan has no standardized statutory payroll deductions
        return {}
