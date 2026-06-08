import unittest
from unittest.mock import MagicMock, patch

from payroll_africa.engine.hooks import get_employee_country, _set_component_amount


class TestGetEmployeeCountry(unittest.TestCase):

	@patch("payroll_africa.engine.hooks.frappe")
	def test_returns_payroll_country(self, mock_frappe):
		"""Should return employee's payroll_country if set."""
		mock_frappe.db.get_value.side_effect = lambda dt, name, field: (
			"Kenya" if dt == "Employee" else "United States"
		)
		result = get_employee_country("EMP-001", "Test Company")
		self.assertEqual(result, "Kenya")

	@patch("payroll_africa.engine.hooks.frappe")
	def test_falls_back_to_company_country(self, mock_frappe):
		"""Should fall back to Company country if payroll_country not set."""
		mock_frappe.db.get_value.side_effect = lambda dt, name, field: (
			None if dt == "Employee" else "Kenya"
		)
		result = get_employee_country("EMP-001", "Test Company")
		self.assertEqual(result, "Kenya")

	@patch("payroll_africa.engine.hooks.frappe")
	def test_returns_none_if_no_country(self, mock_frappe):
		"""Should return None if neither is set."""
		mock_frappe.db.get_value.return_value = None
		result = get_employee_country("EMP-001", "Test Company")
		self.assertIsNone(result)


class TestSetComponentAmount(unittest.TestCase):

	def test_updates_existing_row(self):
		"""Should update amount on existing deduction row."""
		row = MagicMock()
		row.salary_component = "NSSF Employee"
		row.precision.return_value = None

		doc = MagicMock()
		doc.deductions = [row]

		_set_component_amount(doc, "NSSF Employee", 1080, False)
		self.assertEqual(row.amount, 1080.0)
		self.assertEqual(row.default_amount, 1080.0)


class TestRegistryHelpers(unittest.TestCase):

	def test_is_supported_country(self):
		"""Should return True for known countries, False otherwise."""
		from payroll_africa.engine.registry import is_supported_country
		self.assertTrue(is_supported_country("Kenya"))
		self.assertFalse(is_supported_country("Atlantis"))

	def test_get_supported_countries_sorted(self):
		"""Should return a sorted list of all supported countries."""
		from payroll_africa.engine.registry import get_supported_countries
		result = get_supported_countries()
		self.assertEqual(result, sorted(result))
		self.assertIn("Kenya", result)


if __name__ == "__main__":
	unittest.main()
