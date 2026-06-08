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

from payroll_africa.calculators.madagascar import MadagascarCalculator


def make_settings():
	"""Create mock Madagascar Payroll Settings with 2025/2026 rates."""
	settings = MagicMock()
	settings.minimum_wage = 262680
	settings.ceiling_multiplier = 8
	settings.cnaps_employee_rate = 1
	settings.cnaps_employer_rate = 13
	settings.health_employee_rate = 1
	settings.health_employer_rate = 5
	settings.fmfp_rate = 1
	settings.minimum_irsa = 2000
	settings.irsa_bands = []
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


class TestMadagascarCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = MadagascarCalculator(self.settings)

	def test_cnaps_capped(self):
		"""CNaPS at contribution ceiling: 8 x 262,680 = 2,101,440."""
		slip = make_salary_slip(5000000, 4000000)
		results = self.calculator.compute(slip)

		# Ceiling = 8 x 262,680 = 2,101,440
		# Employee: 1% of 2,101,440 = 21,014.40
		expected_employee = 2101440 * 0.01
		self.assertAlmostEqual(results["CNaPS Employee"]["amount"], expected_employee, places=2)

		# Employer: 13% of 2,101,440 = 273,187.20
		expected_employer = 2101440 * 0.13
		self.assertAlmostEqual(results["CNaPS Employer"]["amount"], expected_employer, places=2)
		self.assertFalse(results["CNaPS Employee"]["is_employer_only"])
		self.assertTrue(results["CNaPS Employer"]["is_employer_only"])

	def test_health_contributions(self):
		"""Health insurance contributions at ceiling."""
		slip = make_salary_slip(3000000, 2500000)
		results = self.calculator.compute(slip)

		# At ceiling: 1% employee = 21,014.40; 5% employer = 105,072
		expected_employee = 2101440 * 0.01
		expected_employer = 2101440 * 0.05
		self.assertAlmostEqual(results["Health Insurance Employee"]["amount"], expected_employee, places=2)
		self.assertAlmostEqual(results["Health Insurance Employer"]["amount"], expected_employer, places=2)
		self.assertTrue(results["Health Insurance Employer"]["is_employer_only"])

	def test_irsa_minimum(self):
		"""IRSA minimum amount should be MGA 2,000."""
		slip = make_salary_slip(360000, 350000)
		results = self.calculator.compute(slip)

		irsa = results["IRSA"]["amount"]
		# CNaPS = 1% of 350,000 = 3,500
		# Taxable = 360,000 - 3,500 = 356,500
		# Bracket: (356,500 - 350,000) * 5% = 325, but minimum is 2,000
		self.assertGreaterEqual(irsa, 2000)
		self.assertFalse(results["IRSA"]["is_employer_only"])

	def test_fmfp_employer_only(self):
		"""FMFP is employer only at 1% of gross."""
		slip = make_salary_slip(1000000)
		results = self.calculator.compute(slip)

		self.assertTrue(results["FMFP Training Fund"]["is_employer_only"])
		self.assertEqual(get_amount(results, "FMFP Training Fund"), 10000.0)

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0, 0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "CNaPS Employee"), 0.0)
		self.assertEqual(get_amount(results, "CNaPS Employer"), 0.0)
		self.assertEqual(get_amount(results, "Health Insurance Employee"), 0.0)
		self.assertEqual(get_amount(results, "FMFP Training Fund"), 0.0)
		self.assertEqual(get_amount(results, "IRSA"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(1000000)
		results = self.calculator.compute(slip)

		expected = {
			"CNaPS Employee",
			"CNaPS Employer",
			"Health Insurance Employee",
			"Health Insurance Employer",
			"FMFP Training Fund",
			"IRSA",
		}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
