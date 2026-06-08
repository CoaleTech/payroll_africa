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

from payroll_africa.calculators.tunisia import TunisiaCalculator


def make_settings():
	"""Create mock Tunisia Payroll Settings with 2025/2026 rates."""
	settings = MagicMock()
	settings.cnss_employee_rate = 9.18
	settings.cnss_employer_rate = 17.07
	settings.ssc_rate = 0.5
	settings.professional_deduction_rate = 10
	settings.professional_deduction_cap = 2000
	settings.is_exporting_company = 0
	settings.cnss_employer_export_rate = 16.57
	settings.irpp_bands = []

	# Mock settings.get to return real attribute values
	def _mock_get(key, default=None):
		return getattr(settings, key, default)
	settings.get = _mock_get

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


class TestTunisiaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = TunisiaCalculator(self.settings)

	def test_cnss_computation(self):
		"""CNSS employee and employer contributions."""
		slip = make_salary_slip(3000)
		results = self.calculator.compute(slip)

		# Employee: 9.18% of 3,000 = 275.40
		self.assertEqual(get_amount(results, "CNSS Employee"), 275.40)
		# Employer: 17.07% of 3,000 = 512.10
		self.assertEqual(get_amount(results, "CNSS Employer"), 512.10)
		self.assertFalse(results["CNSS Employee"]["is_employer_only"])
		self.assertTrue(results["CNSS Employer"]["is_employer_only"])

	def test_ssc(self):
		"""Social Solidarity Contribution: 0.5% of gross."""
		slip = make_salary_slip(3000)
		results = self.calculator.compute(slip)

		# 0.5% of 3,000 = 15
		self.assertEqual(get_amount(results, "Social Solidarity Contribution"), 15.0)
		self.assertFalse(results["Social Solidarity Contribution"]["is_employer_only"])

	def test_irpp_positive(self):
		"""IRPP should be positive for a mid-income salary."""
		slip = make_salary_slip(3000)
		results = self.calculator.compute(slip)

		irpp = results["IRPP"]["amount"]
		self.assertGreater(irpp, 0)
		self.assertFalse(results["IRPP"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "CNSS Employee"), 0.0)
		self.assertEqual(get_amount(results, "CNSS Employer"), 0.0)
		self.assertEqual(get_amount(results, "Social Solidarity Contribution"), 0.0)
		self.assertEqual(get_amount(results, "IRPP"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(3000)
		results = self.calculator.compute(slip)

		expected = {"CNSS Employee", "CNSS Employer", "Social Solidarity Contribution", "IRPP"}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
