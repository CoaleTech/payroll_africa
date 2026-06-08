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

from payroll_africa.calculators.egypt import EgyptCalculator


def make_settings():
	"""Create mock Egypt Payroll Settings with 2025/2026 rates."""
	settings = MagicMock()
	settings.social_insurance_employee_rate = 11
	settings.social_insurance_employer_rate = 18.75
	settings.social_insurance_ceiling = 16700
	settings.health_insurance_employee_rate = 1
	settings.health_insurance_employer_rate = 3.25
	settings.personal_exemption = 15000
	settings.number_of_dependents = 0
	settings.max_dependents = 3
	settings.dependent_deduction = 3000
	settings.income_tax_bands = []
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


class TestEgyptCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = EgyptCalculator(self.settings)

	def test_social_insurance_capped(self):
		"""Social insurance capped at EGP 16,700."""
		slip = make_salary_slip(25000, 20000)
		results = self.calculator.compute(slip)

		# Employee: 11% of 16,700 = 1,837
		self.assertEqual(get_amount(results, "Social Insurance Employee"), 1837.0)
		# Employer: 18.75% of 16,700 = 3,131.25
		self.assertEqual(get_amount(results, "Social Insurance Employer"), 3131.25)
		self.assertFalse(results["Social Insurance Employee"]["is_employer_only"])
		self.assertTrue(results["Social Insurance Employer"]["is_employer_only"])

	def test_health_insurance_uncapped(self):
		"""Health insurance has no ceiling."""
		slip = make_salary_slip(25000, 20000)
		results = self.calculator.compute(slip)

		# Employee: 1% of 25,000 = 250
		self.assertEqual(get_amount(results, "Health Insurance Employee"), 250.0)
		# Employer: 3.25% of 25,000 = 812.50
		self.assertEqual(get_amount(results, "Health Insurance Employer"), 812.5)

	def test_martyrs_fund(self):
		"""Martyrs Fund: 0.05% of gross."""
		slip = make_salary_slip(20000, 18000)
		results = self.calculator.compute(slip)

		# 0.05% of 20,000 = 10
		self.assertEqual(get_amount(results, "Martyrs Fund"), 10.0)
		self.assertFalse(results["Martyrs Fund"]["is_employer_only"])

	def test_income_tax_positive(self):
		"""Income tax should be positive for a high salary."""
		slip = make_salary_slip(25000, 20000)
		results = self.calculator.compute(slip)

		income_tax = results["Income Tax"]["amount"]
		self.assertGreater(income_tax, 0)
		self.assertFalse(results["Income Tax"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0, 0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "Social Insurance Employee"), 0.0)
		self.assertEqual(get_amount(results, "Social Insurance Employer"), 0.0)
		self.assertEqual(get_amount(results, "Health Insurance Employee"), 0.0)
		self.assertEqual(get_amount(results, "Martyrs Fund"), 0.0)
		self.assertEqual(get_amount(results, "Income Tax"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(25000, 20000)
		results = self.calculator.compute(slip)

		expected = {
			"Social Insurance Employee",
			"Social Insurance Employer",
			"Health Insurance Employee",
			"Health Insurance Employer",
			"Martyrs Fund",
			"Income Tax",
		}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
