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

from payroll_africa.calculators.botswana import BotswanaCalculator


def make_settings():
	"""Create mock Botswana Payroll Settings with 2025/2026 rates."""
	settings = MagicMock()
	settings.tax_free_threshold = 48000
	settings.paye_bands = []
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


class TestBotswanaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = BotswanaCalculator(self.settings)

	def test_paye_below_threshold(self):
		"""Gross 4,000/month (48,000/year) - exactly at threshold, PAYE should be 0."""
		slip = make_salary_slip(4000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "PAYE"), 0.0)
		self.assertFalse(results["PAYE"]["is_employer_only"])

	def test_paye_middle_income(self):
		"""Gross 15,000/month (180,000/year) - middle income bracket."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		# Taxable = 180,000 - 48,000 = 132,000
		# 36000@5%=1800 + 36000@12.5%=4500 + 36000@18.75%=6750 + 24000@25%=6000
		# Annual tax = 19,050; Monthly = 1,587.50
		expected_monthly = 19050 / 12
		self.assertAlmostEqual(results["PAYE"]["amount"], expected_monthly, places=2)

	def test_paye_above_threshold(self):
		"""Gross 25,000/month (300,000/year) - above threshold."""
		slip = make_salary_slip(25000)
		results = self.calculator.compute(slip)

		# Taxable = 300,000 - 48,000 = 252,000
		# 36000@5% + 36000@12.5% + 36000@18.75% + 36000@25% + 108000@26.5%
		# = 1,800 + 4,500 + 6,750 + 9,000 + 28,620 = 50,670
		expected_monthly = 50670 / 12
		self.assertAlmostEqual(results["PAYE"]["amount"], expected_monthly, places=2)

	def test_zero_salary(self):
		"""PAYE should be 0 when gross is 0."""
		slip = make_salary_slip(0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "PAYE"), 0.0)

	def test_only_paye_exists(self):
		"""Botswana has no social security - only PAYE component."""
		slip = make_salary_slip(10000)
		results = self.calculator.compute(slip)

		self.assertEqual(len(results), 1)
		self.assertIn("PAYE", results)


if __name__ == "__main__":
	unittest.main()
