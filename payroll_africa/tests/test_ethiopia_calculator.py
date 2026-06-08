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

from payroll_africa.calculators.ethiopia import EthiopiaCalculator


def make_settings():
	"""Create mock Ethiopia Payroll Settings with 2025 rates."""
	settings = MagicMock()
	settings.pension_employee_rate = 7
	settings.pension_employer_rate = 11
	settings.pension_ceiling = 15000
	settings.pit_bands = []
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


class TestEthiopiaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = EthiopiaCalculator(self.settings)

	def test_pension_at_cap(self):
		"""Gross 20,000 / Basic 15,000 - pension capped at 15,000."""
		slip = make_salary_slip(20000, 15000)
		results = self.calculator.compute(slip)

		# Employee: 7% of 15,000 = 1,050
		self.assertEqual(get_amount(results, "Pension Employee"), 1050.0)
		# Employer: 11% of 15,000 = 1,650
		self.assertEqual(get_amount(results, "Pension Employer"), 1650.0)
		self.assertFalse(results["Pension Employee"]["is_employer_only"])
		self.assertTrue(results["Pension Employer"]["is_employer_only"])

	def test_pension_below_cap(self):
		"""Gross 10,000 / Basic 10,000 - no cap applied."""
		slip = make_salary_slip(10000, 10000)
		results = self.calculator.compute(slip)

		# Employee: 7% of 10,000 = 700
		self.assertEqual(get_amount(results, "Pension Employee"), 700.0)
		# Employer: 11% of 10,000 = 1,100
		self.assertEqual(get_amount(results, "Pension Employer"), 1100.0)

	def test_pit_progressive(self):
		"""PIT progressive computation for mid-income salary."""
		slip = make_salary_slip(20000, 15000)
		results = self.calculator.compute(slip)

		# Taxable = 20,000 - 1,050 = 18,950
		# Brackets: 2,000@0% + 2,000@15% + 3,000@20% + 3,000@25% + 4,000@30% + 4,950@35%
		# Tax = 0 + 300 + 600 + 750 + 1,200 + 1,732.50 = 4,582.50
		expected_tax = 300 + 600 + 750 + 1200 + 1732.50
		self.assertAlmostEqual(results["PIT"]["amount"], expected_tax, places=2)
		self.assertFalse(results["PIT"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0, 0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "Pension Employee"), 0.0)
		self.assertEqual(get_amount(results, "Pension Employer"), 0.0)
		self.assertEqual(get_amount(results, "PIT"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(20000, 15000)
		results = self.calculator.compute(slip)

		expected = {"Pension Employee", "Pension Employer", "PIT"}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
