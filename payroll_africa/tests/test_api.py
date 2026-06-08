import sys
import unittest
from unittest.mock import MagicMock, patch


# Force-install frappe mock before importing the api module.
# Use sys.modules[] assignment (not setdefault) so this takes effect even
# when the bench test runner has already loaded real frappe.
# We also force-delete any cached payroll_africa.api so it re-imports with
# the mock active.
_mock_frappe = MagicMock()
_mock_frappe._ = lambda x: x
_mock_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)  # passthrough decorator
_mock_frappe.utils.flt = lambda x, precision=None: round(float(x or 0), precision or 9)
_mock_frappe._dict = dict  # frappe._dict is a dict subclass; plain dict is fine here
_mock_frappe.has_permission = MagicMock(return_value=True)
_mock_frappe.throw = MagicMock(side_effect=None)

sys.modules["frappe"] = _mock_frappe
sys.modules["frappe.utils"] = _mock_frappe.utils

# Force-reimport so the module picks up the mock whitelist decorator
for mod in list(sys.modules):
	if mod.startswith("payroll_africa.api"):
		del sys.modules[mod]

from payroll_africa.api import calculate_deductions, get_supported_countries  # noqa: E402
from payroll_africa.engine.registry import COUNTRY_MAP  # noqa: E402


class TestGetSupportedCountries(unittest.TestCase):

	def test_returns_sorted_countries(self):
		result = get_supported_countries()
		self.assertEqual(result, sorted(COUNTRY_MAP.keys()))
		self.assertEqual(len(result), len(COUNTRY_MAP))  # 54 countries

	def test_includes_all_countries(self):
		result = get_supported_countries()
		for country in ["Kenya", "Uganda", "Tanzania", "Rwanda", "Nigeria", "Angola"]:
			self.assertIn(country, result)

	def test_includes_new_tier2_countries(self):
		result = get_supported_countries()
		for country in ["Algeria", "Senegal", "Cameroon", "Mauritius", "Zimbabwe", "Mali"]:
			self.assertIn(country, result)

	def test_is_sorted(self):
		result = get_supported_countries()
		self.assertEqual(result, sorted(result))


class TestCalculateDeductions(unittest.TestCase):

	def setUp(self):
		_mock_frappe.throw.side_effect = None

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
		self.assertAlmostEqual(result["employee_total"], 2455.0)
		self.assertAlmostEqual(result["employer_total"], 1080.0)
		self.assertAlmostEqual(result["net_pay"], 47545.0)
		self.assertAlmostEqual(result["cost_to_company"], 51080.0)

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

	@patch("payroll_africa.api.get_calculator")
	def test_missing_settings(self, mock_get_calc):
		"""Should throw when calculator cannot be built."""
		mock_get_calc.return_value = None
		_mock_frappe.throw.side_effect = Exception("No settings")
		with self.assertRaises(Exception):
			calculate_deductions("Kenya", 50000)

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
		"""Each deduction dict must have component, amount, is_employer_only."""
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
