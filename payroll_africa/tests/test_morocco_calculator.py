import unittest
from unittest.mock import MagicMock

# Mock frappe before importing calculators
import sys
sys.modules["frappe"] = MagicMock()
sys.modules["frappe.utils"] = MagicMock()


def mock_flt(value, precision=None):
	if value is None:
		return 0.0
	return float(value)


sys.modules["frappe.utils"].flt = mock_flt

from payroll_africa.calculators.morocco import MoroccoCalculator


def make_settings():
	"""Create mock Morocco Payroll Settings with 2026 rates."""
	settings = MagicMock()
	settings.cnss_ceiling = 6000
	settings.cnss_capped_rate = 4.48
	settings.cnss_uncapped_rate = 2.26
	settings.cnss_employer_capped_rate = 8.6
	settings.cnss_employer_uncapped_rate = 4.11
	settings.professional_deduction_rate = 20
	settings.professional_deduction_ceiling = 2500
	settings.annual_exemption = 40000
	settings.number_of_dependents = 0
	settings.max_dependents_for_allowance = 6
	settings.dependent_allowance = 500
	settings.ir_bands = []
	return settings


def make_salary_slip(gross_pay, basic_pay=None):
	"""Create mock Salary Slip."""
	slip = MagicMock()
	slip.gross_pay = gross_pay
	slip.earnings = []
	if basic_pay is not None:
		earning = MagicMock()
		earning.salary_component = "Basic Salary"
		earning.amount = basic_pay
		slip.earnings.append(earning)
	return slip


def get_amount(results, key):
	return round(results[key]["amount"], 2)


class TestMoroccoCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = MoroccoCalculator(self.settings)

	def test_cnss_capped(self):
		"""CNSS capped and uncapped portions for gross above ceiling."""
		slip = make_salary_slip(10000)
		results = self.calculator.compute(slip)

		# Capped: 4.48% of 6,000 = 268.80
		# Uncapped: 2.26% of 10,000 = 226
		# Total employee CNSS = 494.80
		expected_cnss = 268.80 + 226
		self.assertEqual(get_amount(results, "CNSS Employee"), expected_cnss)

		# Employer capped: 8.6% of 6,000 = 516
		# Employer uncapped: 4.11% of 10,000 = 411
		# Total employer CNSS = 927
		expected_empr = 516 + 411
		self.assertEqual(get_amount(results, "CNSS Employer"), expected_empr)
		self.assertTrue(results["CNSS Employer"]["is_employer_only"])

	def test_cnss_below_cap(self):
		"""CNSS when gross is below the ceiling."""
		slip = make_salary_slip(5000)
		results = self.calculator.compute(slip)

		# Capped: 4.48% of 5,000 = 224
		# Uncapped: 2.26% of 5,000 = 113
		self.assertEqual(get_amount(results, "CNSS Employee"), 337.0)

	def test_ir_calculation(self):
		"""IR should be positive for a mid-income salary."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		ir = results["IR"]["amount"]
		self.assertGreater(ir, 0)
		self.assertFalse(results["IR"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "CNSS Employee"), 0.0)
		self.assertEqual(get_amount(results, "CNSS Employer"), 0.0)
		self.assertEqual(get_amount(results, "IR"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		expected = {"CNSS Employee", "CNSS Employer", "IR"}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
