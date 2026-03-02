import frappe
from frappe.utils import flt


class BaseCalculator:
	"""Base class for country-specific statutory deduction calculators."""

	def __init__(self, settings):
		self.settings = settings

	def compute(self, salary_slip):
		"""
		Compute all statutory deductions for this country.

		Args:
			salary_slip: The Salary Slip document (with gross_pay set)

		Returns:
			dict: {
				"component_name": {
					"amount": float,
					"is_employer_only": bool,
				}
			}
		"""
		raise NotImplementedError

	def get_gross_pay(self, salary_slip):
		return flt(salary_slip.gross_pay)

	def get_basic_pay(self, salary_slip):
		"""Get basic salary from earnings."""
		for earning in salary_slip.earnings:
			if earning.salary_component == "Basic Salary":
				return flt(earning.amount)
		return 0
