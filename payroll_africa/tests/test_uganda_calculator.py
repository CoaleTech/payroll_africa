import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.uganda import UgandaCalculator


class TestUgandaCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.nssf_employee_rate = 5
		self.settings.nssf_employer_rate = 10
		self.settings.lst_annual_amount = 100000
		self.calculator = UgandaCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_nssf_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NSSF Employee UG"]["amount"], 50000)
		self.assertFalse(result["NSSF Employee UG"]["is_employer_only"])

	def test_nssf_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NSSF Employer UG"]["amount"], 100000)
		self.assertTrue(result["NSSF Employer UG"]["is_employer_only"])

	def test_lst_monthly(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["LST"]["amount"], 100000 / 12)
		self.assertFalse(result["LST"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["NSSF Employee UG"]["amount"], 0)
		self.assertEqual(result["NSSF Employer UG"]["amount"], 0)
		# LST is still charged even with zero gross (flat tax)
		self.assertAlmostEqual(result["LST"]["amount"], 100000 / 12)

	def test_nssf_rates_proportional(self):
		"""Employer NSSF should be double the employee NSSF (10% vs 5%)."""
		result = self.calculator.compute(self._make_slip(500000))
		self.assertAlmostEqual(
			result["NSSF Employer UG"]["amount"],
			result["NSSF Employee UG"]["amount"] * 2,
		)


if __name__ == "__main__":
	unittest.main()
