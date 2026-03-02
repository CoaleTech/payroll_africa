import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.zambia import ZambiaCalculator


class TestZambiaCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.napsa_employee_rate = 5
		self.settings.napsa_employer_rate = 5
		self.settings.napsa_cap = 8541
		self.settings.nhima_employee_rate = 1
		self.settings.nhima_employer_rate = 1
		self.calculator = ZambiaCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_napsa_employee_under_cap(self):
		result = self.calculator.compute(self._make_slip(5000))
		self.assertAlmostEqual(result["NAPSA Employee ZM"]["amount"], 250)  # 5000 * 5%
		self.assertFalse(result["NAPSA Employee ZM"]["is_employer_only"])

	def test_napsa_employee_over_cap(self):
		result = self.calculator.compute(self._make_slip(20000))
		self.assertAlmostEqual(result["NAPSA Employee ZM"]["amount"], 427.05)  # 8541 * 5%
		self.assertFalse(result["NAPSA Employee ZM"]["is_employer_only"])

	def test_napsa_employer_over_cap(self):
		result = self.calculator.compute(self._make_slip(20000))
		self.assertAlmostEqual(result["NAPSA Employer ZM"]["amount"], 427.05)  # 8541 * 5%
		self.assertTrue(result["NAPSA Employer ZM"]["is_employer_only"])

	def test_nhima_employee_no_cap(self):
		result = self.calculator.compute(self._make_slip(20000))
		self.assertAlmostEqual(result["NHIMA Employee ZM"]["amount"], 200)  # 20000 * 1%
		self.assertFalse(result["NHIMA Employee ZM"]["is_employer_only"])

	def test_nhima_employer_no_cap(self):
		result = self.calculator.compute(self._make_slip(20000))
		self.assertAlmostEqual(result["NHIMA Employer ZM"]["amount"], 200)  # 20000 * 1%
		self.assertTrue(result["NHIMA Employer ZM"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["NAPSA Employee ZM"]["amount"], 0)
		self.assertEqual(result["NAPSA Employer ZM"]["amount"], 0)
		self.assertEqual(result["NHIMA Employee ZM"]["amount"], 0)
		self.assertEqual(result["NHIMA Employer ZM"]["amount"], 0)

	def test_all_components_returned(self):
		result = self.calculator.compute(self._make_slip(10000))
		expected = {"NAPSA Employee ZM", "NAPSA Employer ZM", "NHIMA Employee ZM", "NHIMA Employer ZM"}
		self.assertEqual(set(result.keys()), expected)


if __name__ == "__main__":
	unittest.main()
