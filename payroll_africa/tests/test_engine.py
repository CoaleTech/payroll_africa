import unittest
from unittest.mock import MagicMock, patch

from payroll_africa.engine.hooks import get_employee_country
from payroll_africa.engine.salary_slip import (
	_set_component_amount,
	apply_regional_deductions,
)


class TestGetEmployeeCountry(unittest.TestCase):

	@patch("payroll_africa.engine.hooks.frappe")
	@patch("payroll_africa.engine.hooks.get_effective_ssa_values")
	def test_prefers_ssa_payroll_country(self, mock_get_ssa, mock_frappe):
		"""Should prefer Salary Structure Assignment payroll_country when available."""
		mock_get_ssa.return_value = {"payroll_country": "Uganda"}
		mock_frappe.db.get_value.return_value = "Kenya"

		result = get_employee_country(
			"EMP-001", "Test Company", "SS-001", "2025-06-01"
		)
		self.assertEqual(result, "Uganda")
		mock_get_ssa.assert_called_once()

	@patch("payroll_africa.engine.hooks.frappe")
	@patch("payroll_africa.engine.hooks.get_effective_ssa_values")
	def test_returns_payroll_country(self, mock_get_ssa, mock_frappe):
		"""Should return employee's payroll_country if SSA country is not set."""
		mock_get_ssa.return_value = {}
		mock_frappe.db.get_value.side_effect = lambda dt, name, field: (
			"Kenya" if dt == "Employee" else "United States"
		)
		result = get_employee_country("EMP-001", "Test Company")
		self.assertEqual(result, "Kenya")

	@patch("payroll_africa.engine.hooks.frappe")
	@patch("payroll_africa.engine.hooks.get_effective_ssa_values")
	def test_falls_back_to_company_country(self, mock_get_ssa, mock_frappe):
		"""Should fall back to Company country if payroll_country not set."""
		mock_get_ssa.return_value = {}
		mock_frappe.db.get_value.side_effect = lambda dt, name, field: (
			None if dt == "Employee" else "Kenya"
		)
		result = get_employee_country("EMP-001", "Test Company")
		self.assertEqual(result, "Kenya")

	@patch("payroll_africa.engine.hooks.frappe")
	@patch("payroll_africa.engine.hooks.get_effective_ssa_values")
	def test_returns_none_if_no_country(self, mock_get_ssa, mock_frappe):
		"""Should return None if neither is set."""
		mock_get_ssa.return_value = {}
		mock_frappe.db.get_value.return_value = None
		result = get_employee_country("EMP-001", "Test Company")
		self.assertIsNone(result)


class TestApplyRegionalDeductions(unittest.TestCase):

	@patch("payroll_africa.engine.salary_slip._set_component_amount")
	@patch("payroll_africa.engine.salary_slip.get_calculator")
	@patch("payroll_africa.engine.salary_slip._is_country_enabled")
	@patch("payroll_africa.engine.salary_slip.get_employee_country")
	def test_hook_injects_components(
		self, mock_country, mock_enabled, mock_get_calculator, mock_set_amount
	):
		"""Regional override should compute and inject statutory rows."""
		mock_country.return_value = "Kenya"
		mock_enabled.return_value = True
		mock_calc = MagicMock()
		mock_calc.compute.return_value = {
			"NSSF Employee": {"amount": 1080, "is_employer_only": False},
			"NSSF Employer": {"amount": 1080, "is_employer_only": True},
		}
		mock_get_calculator.return_value = mock_calc

		doc = MagicMock()
		doc.employee = "EMP-001"
		doc.company = "Test Company"
		doc.salary_structure = "SS-001"
		doc.start_date = "2025-06-01"

		apply_regional_deductions(doc)

		mock_set_amount.assert_any_call(doc, "NSSF Employee", 1080, False)
		mock_set_amount.assert_any_call(doc, "NSSF Employer", 1080, True)

	@patch("payroll_africa.engine.salary_slip._set_component_amount")
	@patch("payroll_africa.engine.salary_slip.get_calculator")
	@patch("payroll_africa.engine.salary_slip._is_country_enabled")
	@patch("payroll_africa.engine.salary_slip.get_employee_country")
	def test_hook_exits_when_country_disabled(
		self, mock_country, mock_enabled, mock_get_calculator, mock_set_amount
	):
		"""Regional override should exit when country is not enabled."""
		mock_country.return_value = "Kenya"
		mock_enabled.return_value = False

		doc = MagicMock()
		doc.employee = "EMP-001"
		doc.company = "Test Company"
		doc.salary_structure = "SS-001"
		doc.start_date = "2025-06-01"

		apply_regional_deductions(doc)

		mock_get_calculator.assert_not_called()
		mock_set_amount.assert_not_called()


class TestSetComponentAmount(unittest.TestCase):

	def test_updates_existing_deduction_row(self):
		"""Should update amount on existing deduction row."""
		row = MagicMock()
		row.salary_component = "NSSF Employee"
		row.precision.return_value = None

		doc = MagicMock()
		doc.deductions = [row]
		doc.get.return_value = [row]

		_set_component_amount(doc, "NSSF Employee", 1080, False)
		self.assertEqual(row.amount, 1080.0)
		self.assertEqual(row.default_amount, 1080.0)

	@patch("payroll_africa.engine.salary_slip.frappe")
	def test_employer_component_goes_to_employer_contributions(self, mock_frappe):
		"""Employer-only components should land in employer_contributions."""
		mock_frappe.db.exists.return_value = True
		mock_component = MagicMock()
		mock_component.salary_component_abbr = "NSSFr"
		mock_component.exempted_from_income_tax = 0
		mock_frappe.get_cached_doc.return_value = mock_component

		meta = MagicMock()
		field = MagicMock()
		field.fieldname = "employer_contributions"
		field.options = "Salary Detail"
		meta.get_table_fields.return_value = [field]
		mock_frappe.get_meta.return_value = meta

		doc = MagicMock()
		doc.deductions = []
		doc.employer_contributions = []
		doc.get.side_effect = lambda key: getattr(doc, key, None)
		doc.append.side_effect = lambda table, row: getattr(doc, table).append(row)

		_set_component_amount(doc, "NSSF Employer", 1080, True)

		self.assertEqual(len(doc.deductions), 0)
		self.assertEqual(len(doc.employer_contributions), 1)
		appended = doc.employer_contributions[0]
		self.assertEqual(appended["salary_component"], "NSSF Employer")
		self.assertEqual(appended["amount"], 1080.0)
		self.assertNotIn("statistical_component", appended)
		self.assertNotIn("do_not_include_in_total", appended)

	@patch("payroll_africa.engine.salary_slip.frappe")
	def test_employer_component_falls_back_to_deductions(self, mock_frappe):
		"""If Salary Slip lacks employer_contributions, employer costs fall back."""
		mock_frappe.db.exists.return_value = True
		mock_component = MagicMock()
		mock_component.salary_component_abbr = "NSSFr"
		mock_component.exempted_from_income_tax = 0
		mock_frappe.get_cached_doc.return_value = mock_component

		meta = MagicMock()
		meta.get_table_fields.return_value = []
		mock_frappe.get_meta.return_value = meta

		doc = MagicMock()
		doc.deductions = []
		doc.get.side_effect = lambda key: getattr(doc, key, None)
		doc.append.side_effect = lambda table, row: getattr(doc, table).append(row)

		_set_component_amount(doc, "NSSF Employer", 1080, True)

		self.assertEqual(len(doc.deductions), 1)
		appended = doc.deductions[0]
		self.assertEqual(appended["statistical_component"], 1)
		self.assertEqual(appended["do_not_include_in_total"], 1)


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
