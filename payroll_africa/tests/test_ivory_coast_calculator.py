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

from payroll_africa.calculators.ivory_coast import IvoryCoastCalculator


def make_settings():
	"""Create mock Ivory Coast Payroll Settings with 2025/2026 rates."""
	settings = MagicMock()
	settings.cnps_ceiling = 3375000
	settings.cnps_employee_rate = 6.3
	settings.cnps_employer_rate = 7.7
	settings.family_allowances_rate = 5.75
	settings.work_injury_risk_class = 1
	settings.training_tax_rate = 1.2
	settings.housing_fund_rate = 1.5
	settings.standard_deduction_rate = 20
	settings.family_shares = 1
	settings.max_shares = 5
	settings.tax_credit_per_share = 5500
	settings.its_bands = []
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


class TestIvoryCoastCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = IvoryCoastCalculator(self.settings)

	def test_cnps_retirement_capped(self):
		"""CNPS retirement capped at XOF 3,375,000."""
		slip = make_salary_slip(5000000, 4000000)
		results = self.calculator.compute(slip)

		# Employee: 6.3% of 3,375,000 = 212,625
		self.assertEqual(get_amount(results, "CNPS Retirement Employee"), 212625.0)
		# Employer: 7.7% of 3,375,000 = 259,875
		self.assertEqual(get_amount(results, "CNPS Retirement Employer"), 259875.0)
		self.assertFalse(results["CNPS Retirement Employee"]["is_employer_only"])
		self.assertTrue(results["CNPS Retirement Employer"]["is_employer_only"])

	def test_employer_contributions(self):
		"""All employer-only contributions should be flagged correctly."""
		slip = make_salary_slip(5000000, 4000000)
		results = self.calculator.compute(slip)

		self.assertTrue(results["CNPS Family Allowances"]["is_employer_only"])
		self.assertTrue(results["Work Injury Insurance"]["is_employer_only"])
		self.assertTrue(results["Vocational Training Tax"]["is_employer_only"])
		self.assertTrue(results["Housing Construction Fund"]["is_employer_only"])

		# Family: 5.75% of 5,000,000 = 287,500
		self.assertEqual(get_amount(results, "CNPS Family Allowances"), 287500.0)
		# Work injury (class 1): 2% of 5,000,000 = 100,000
		self.assertEqual(get_amount(results, "Work Injury Insurance"), 100000.0)
		# Training: 1.2% of 5,000,000 = 60,000
		self.assertEqual(get_amount(results, "Vocational Training Tax"), 60000.0)
		# Housing: 1.5% of 5,000,000 = 75,000
		self.assertEqual(get_amount(results, "Housing Construction Fund"), 75000.0)

	def test_its_with_standard_deduction(self):
		"""ITS with 20% standard deduction."""
		slip = make_salary_slip(2000000)
		results = self.calculator.compute(slip)

		# After 20% deduction: taxable = 1,600,000
		# Brackets: 150,000@0% + 150,000@12% + 200,000@18% + 500,000@25% + 600,000@30%
		# Tax = 0 + 18,000 + 36,000 + 125,000 + 180,000 = 359,000
		# Credit: 1 * 5,500 = 5,500
		# Final = 353,500
		expected = 18000 + 36000 + 125000 + 180000 - 5500
		self.assertEqual(get_amount(results, "ITS"), expected)
		self.assertFalse(results["ITS"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0, 0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "CNPS Retirement Employee"), 0.0)
		self.assertEqual(get_amount(results, "CNPS Retirement Employer"), 0.0)
		self.assertEqual(get_amount(results, "ITS"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(2000000)
		results = self.calculator.compute(slip)

		expected = {
			"CNPS Retirement Employee",
			"CNPS Retirement Employer",
			"CNPS Family Allowances",
			"Work Injury Insurance",
			"Vocational Training Tax",
			"Housing Construction Fund",
			"ITS",
		}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
