import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.mozambique import MozambiqueCalculator


class TestMozambiqueCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.inss_employee_rate = 3
		self.settings.inss_employer_rate = 4
		self.calculator = MozambiqueCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_inss_employee(self):
		result = self.calculator.compute(self._make_slip(500000))
		self.assertAlmostEqual(result["INSS Employee MZ"]["amount"], 15000)
		self.assertFalse(result["INSS Employee MZ"]["is_employer_only"])

	def test_inss_employer(self):
		result = self.calculator.compute(self._make_slip(500000))
		self.assertAlmostEqual(result["INSS Employer MZ"]["amount"], 20000)
		self.assertTrue(result["INSS Employer MZ"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["INSS Employee MZ"]["amount"], 0)
		self.assertEqual(result["INSS Employer MZ"]["amount"], 0)

	def test_all_components_returned(self):
		result = self.calculator.compute(self._make_slip(500000))
		self.assertEqual(len(result), 2)
		self.assertIn("INSS Employee MZ", result)
		self.assertIn("INSS Employer MZ", result)


if __name__ == "__main__":
	unittest.main()
