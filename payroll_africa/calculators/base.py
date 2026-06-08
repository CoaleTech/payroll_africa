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
		"""Extract basic salary from earnings table, fallback to gross_pay."""
		for row in salary_slip.earnings or []:
			if getattr(row, "salary_component", "") == "Basic Salary":
				return flt(row.amount)
		return self.get_gross_pay(salary_slip)

	def validate_settings(self):
		"""Validate that all required settings fields are present.

		Override in subclass to add country-specific validation.
		Raises frappe.ValidationError if settings are incomplete.
		"""
		pass
