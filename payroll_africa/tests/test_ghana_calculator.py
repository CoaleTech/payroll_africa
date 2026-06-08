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

from payroll_africa.calculators.ghana import GhanaCalculator


def make_settings():
	"""Create mock Ghana Payroll Settings with 2025/2026 rates."""
	settings = MagicMock()
	settings.ssnit_employee_rate = 5.5
	settings.ssnit_employer_rate = 13
	settings.tier2_employer_rate = 5
	settings.ssnit_ceiling = 0
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


class TestGhanaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = GhanaCalculator(self.settings)

	def test_ssnit_employee(self):
		"""SSNIT employee: 5.5% of basic salary."""
		slip = make_salary_slip(8000, 6000)
		results = self.calculator.compute(slip)

		# 5.5% of 6,000 = 330
		self.assertEqual(get_amount(results, "SSNIT Employee"), 330.0)
		self.assertFalse(results["SSNIT Employee"]["is_employer_only"])

	def test_ssnit_employer(self):
		"""SSNIT employer: 13% of basic; Tier 2: 5% of basic."""
		slip = make_salary_slip(8000, 6000)
		results = self.calculator.compute(slip)

		# Employer SSNIT: 13% of 6,000 = 780
		self.assertEqual(get_amount(results, "SSNIT Employer"), 780.0)
		# Tier 2: 5% of 6,000 = 300
		self.assertEqual(get_amount(results, "Tier 2 Pension Employer"), 300.0)
		self.assertTrue(results["SSNIT Employer"]["is_employer_only"])
		self.assertTrue(results["Tier 2 Pension Employer"]["is_employer_only"])

	def test_paye_after_ssnit(self):
		"""PAYE calculated after SSNIT deduction."""
		slip = make_salary_slip(8000, 6000)
		results = self.calculator.compute(slip)

		ssnit = results["SSNIT Employee"]["amount"]
		paye = results["PAYE"]["amount"]
		# Chargeable = 8,000 - 330 = 7,670 monthly = 92,040 annual
		# First 5,880@0% + 1,320@5% + 1,560@10% + 38,000@17.5% + 45,280@25%
		# Tax = 0 + 66 + 156 + 6,650 + 11,320 = 18,192 annual = 1,516 monthly
		self.assertGreater(paye, 0)
		self.assertFalse(results["PAYE"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0, 0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "SSNIT Employee"), 0.0)
		self.assertEqual(get_amount(results, "SSNIT Employer"), 0.0)
		self.assertEqual(get_amount(results, "Tier 2 Pension Employer"), 0.0)
		self.assertEqual(get_amount(results, "PAYE"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(8000, 6000)
		results = self.calculator.compute(slip)

		expected = {"SSNIT Employee", "SSNIT Employer", "Tier 2 Pension Employer", "PAYE"}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
