import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.angola import AngolaCalculator


class TestAngolaCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.inss_employee_rate = 3
		self.settings.inss_employer_rate = 8
		self.calculator = AngolaCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_inss_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["INSS Employee AO"]["amount"], 30000)
		self.assertFalse(result["INSS Employee AO"]["is_employer_only"])

	def test_inss_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["INSS Employer AO"]["amount"], 80000)
		self.assertTrue(result["INSS Employer AO"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["INSS Employee AO"]["amount"], 0)
		self.assertEqual(result["INSS Employer AO"]["amount"], 0)

	def test_all_components_returned(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertEqual(len(result), 2)


if __name__ == "__main__":
	unittest.main()
