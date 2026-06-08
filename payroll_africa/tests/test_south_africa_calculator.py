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

# Prevent frappe.db.get_value from returning a truthy MagicMock in _get_employee_age
sys.modules["frappe"].db.get_value.return_value = None

from payroll_africa.calculators.south_africa import SouthAfricaCalculator


def make_settings():
	"""Create mock South Africa Payroll Settings with 2024/2025 rates."""
	settings = MagicMock()
	settings.uif_ceiling = 17712
	settings.uif_rate = 1
	settings.sdl_applicable = 1
	settings.sdl_rate = 1
	settings.rebate_primary = 17235
	settings.threshold_under_65 = 95750
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


class TestSouthAfricaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = SouthAfricaCalculator(self.settings)

	def test_uif_capped(self):
		"""UIF capped at R17,712 x 1% = R177.12."""
		slip = make_salary_slip(25000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "UIF Employee"), 177.12)
		self.assertEqual(get_amount(results, "UIF Employer"), 177.12)
		self.assertFalse(results["UIF Employee"]["is_employer_only"])
		self.assertTrue(results["UIF Employer"]["is_employer_only"])

	def test_uif_below_cap(self):
		"""UIF below ceiling: 1% of gross."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "UIF Employee"), 150.0)
		self.assertEqual(get_amount(results, "UIF Employer"), 150.0)

	def test_sdl_applied(self):
		"""SDL is 1% of gross when applicable."""
		slip = make_salary_slip(20000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "SDL"), 200.0)
		self.assertTrue(results["SDL"]["is_employer_only"])

	def test_paye_progressive(self):
		"""PAYE should be positive for a mid-income salary."""
		slip = make_salary_slip(30000)
		results = self.calculator.compute(slip)

		paye = results["PAYE"]["amount"]
		self.assertGreater(paye, 0)
		self.assertFalse(results["PAYE"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "UIF Employee"), 0.0)
		self.assertEqual(get_amount(results, "UIF Employer"), 0.0)
		self.assertNotIn("SDL", results)
		self.assertEqual(get_amount(results, "PAYE"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(30000)
		results = self.calculator.compute(slip)

		expected = {"UIF Employee", "UIF Employer", "SDL", "PAYE"}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
