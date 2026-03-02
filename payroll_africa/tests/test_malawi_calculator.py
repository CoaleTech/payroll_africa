import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.malawi import MalawiCalculator


class TestMalawiCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.pension_employee_rate = 5
		self.settings.pension_employer_rate = 10
		self.calculator = MalawiCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_pension_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Pension Employee MW"]["amount"], 50000)
		self.assertFalse(result["Pension Employee MW"]["is_employer_only"])

	def test_pension_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Pension Employer MW"]["amount"], 100000)
		self.assertTrue(result["Pension Employer MW"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["Pension Employee MW"]["amount"], 0)
		self.assertEqual(result["Pension Employer MW"]["amount"], 0)

	def test_all_components_returned(self):
		result = self.calculator.compute(self._make_slip(500000))
		expected = {"Pension Employee MW", "Pension Employer MW"}
		self.assertEqual(set(result.keys()), expected)


if __name__ == "__main__":
	unittest.main()
