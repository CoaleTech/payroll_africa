import frappe
from frappe.utils import flt


class BaseCalculator:
	"""Base class for country-specific statutory deduction calculators."""

	def __init__(self, settings):
		self.settings = settings

	def compute(self, salary_slip):
		"""Compute all statutory deductions for this country.

		Args:
			salary_slip: The Salary Slip document (with gross_pay set)
		Returns:
			dict: {"component_name": {"amount": float, "is_employer_only": bool}}
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

	def _compute_tax_from_bands(self, annual, bands):
		"""Compute annual tax from a settings band table.

		Args:
			annual: annualised taxable income
			bands:  list of band objects with from_amount, to_amount, rate
			        (rate is a percentage, e.g. 15 means 15%)
		Returns:
			annual tax amount (float)
		"""
		tax = 0.0
		for band in bands:
			lower = flt(band.from_amount)
			upper = flt(band.to_amount)
			rate = flt(band.rate) / 100.0
			if annual <= lower:
				break
			top = upper if upper > 0 else annual
			amount = min(annual, top) - lower
			if amount > 0:
				tax += amount * rate
		return tax

	def validate_settings(self):
		"""Validate required settings fields.

		Override in subclass to add country-specific validation.
		"""
		pass
