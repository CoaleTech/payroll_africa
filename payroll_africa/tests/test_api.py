import sys
import unittest
from unittest.mock import MagicMock, patch


# Mock frappe before importing api module so @frappe.whitelist() is a no-op
_mock_frappe = MagicMock()
_mock_frappe._ = lambda x: x
_mock_frappe.whitelist = lambda *a, **kw: lambda fn: fn  # decorator passthrough
_mock_frappe.utils.flt = lambda x, precision=None: round(float(x or 0), precision or 9)
sys.modules.setdefault("frappe", _mock_frappe)
sys.modules.setdefault("frappe.utils", _mock_frappe.utils)

from payroll_africa.api import calculate_deductions, get_supported_countries
from payroll_africa.engine.registry import _country_map


class TestGetSupportedCountries(unittest.TestCase):

	def test_returns_sorted_countries(self):
		result = get_supported_countries()
		self.assertEqual(result, sorted(_country_map.keys()))
		self.assertEqual(len(result), 11)

	def test_includes_all_countries(self):
		result = get_supported_countries()
		for country in ["Kenya", "Uganda", "Tanzania", "Rwanda", "Nigeria", "Angola"]:
			self.assertIn(country, result)


class TestCalculateDeductions(unittest.TestCase):

	@patch("payroll_africa.api.get_calculator")
	def test_valid_country(self, mock_get_calc):
		"""Should return deductions for a valid country."""
		mock_calc = MagicMock()
		mock_calc.compute.return_value = {
			"NSSF Employee": {"amount": 1080, "is_employer_only": False},
			"NSSF Employer": {"amount": 1080, "is_employer_only": True},
			"SHIF": {"amount": 1375, "is_employer_only": False},
		}
		mock_get_calc.return_value = mock_calc

		result = calculate_deductions("Kenya", 50000)

		self.assertEqual(result["country"], "Kenya")
		self.assertEqual(result["gross_pay"], 50000)
		self.assertEqual(result["basic_pay"], 50000)
		self.assertEqual(len(result["deductions"]), 3)
		self.assertEqual(result["employee_total"], 2455.0)
		self.assertEqual(result["employer_total"], 1080.0)
		self.assertEqual(result["net_pay"], 47545.0)
		self.assertEqual(result["cost_to_company"], 51080.0)

	@patch("payroll_africa.api.get_calculator")
	def test_custom_basic_pay(self, mock_get_calc):
		"""Should pass basic_pay separately from gross_pay."""
		mock_calc = MagicMock()
		mock_calc.compute.return_value = {}
		mock_get_calc.return_value = mock_calc

		result = calculate_deductions("Kenya", 100000, basic_pay=60000)

		self.assertEqual(result["gross_pay"], 100000)
		self.assertEqual(result["basic_pay"], 60000)
		self.assertEqual(result["net_pay"], 100000)  # no deductions

	def test_unsupported_country(self):
		"""Should throw for unsupported country."""
		_mock_frappe.throw.side_effect = Exception("Not supported")
		with self.assertRaises(Exception):
			calculate_deductions("Atlantis", 50000)
		_mock_frappe.throw.side_effect = None

	@patch("payroll_africa.api.get_calculator")
	def test_missing_settings(self, mock_get_calc):
		"""Should throw when country settings not found."""
		mock_get_calc.return_value = None
		_mock_frappe.throw.side_effect = Exception("No settings")
		with self.assertRaises(Exception):
			calculate_deductions("Kenya", 50000)
		_mock_frappe.throw.side_effect = None

	@patch("payroll_africa.api.get_calculator")
	def test_zero_gross_pay(self, mock_get_calc):
		"""Should handle zero gross pay."""
		mock_calc = MagicMock()
		mock_calc.compute.return_value = {
			"SHIF": {"amount": 0, "is_employer_only": False},
		}
		mock_get_calc.return_value = mock_calc

		result = calculate_deductions("Kenya", 0)
		self.assertEqual(result["net_pay"], 0)
		self.assertEqual(result["cost_to_company"], 0)

	@patch("payroll_africa.api.get_calculator")
	def test_employer_only_not_in_net_pay(self, mock_get_calc):
		"""Employer-only deductions should not reduce net pay."""
		mock_calc = MagicMock()
		mock_calc.compute.return_value = {
			"NITA": {"amount": 50, "is_employer_only": True},
		}
		mock_get_calc.return_value = mock_calc

		result = calculate_deductions("Kenya", 100000)
		self.assertEqual(result["employee_total"], 0)
		self.assertEqual(result["employer_total"], 50)
		self.assertEqual(result["net_pay"], 100000)
		self.assertEqual(result["cost_to_company"], 100050)

	@patch("payroll_africa.api.get_calculator")
	def test_deduction_structure(self, mock_get_calc):
		"""Each deduction should have component, amount, is_employer_only."""
		mock_calc = MagicMock()
		mock_calc.compute.return_value = {
			"NSSF Employee": {"amount": 1080, "is_employer_only": False},
		}
		mock_get_calc.return_value = mock_calc

		result = calculate_deductions("Kenya", 50000)
		deduction = result["deductions"][0]
		self.assertEqual(deduction["component"], "NSSF Employee")
		self.assertEqual(deduction["amount"], 1080)
		self.assertFalse(deduction["is_employer_only"])


if __name__ == "__main__":
	unittest.main()
