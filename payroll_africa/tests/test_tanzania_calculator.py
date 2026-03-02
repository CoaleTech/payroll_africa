import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.tanzania import TanzaniaCalculator


class TestTanzaniaCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.nssf_employee_rate = 10
		self.settings.nssf_employer_rate = 10
		self.settings.sdl_rate = 3.5
		self.settings.wcf_rate = 0.5
		self.calculator = TanzaniaCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_nssf_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NSSF Employee TZ"]["amount"], 100000)
		self.assertFalse(result["NSSF Employee TZ"]["is_employer_only"])

	def test_nssf_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NSSF Employer TZ"]["amount"], 100000)
		self.assertTrue(result["NSSF Employer TZ"]["is_employer_only"])

	def test_sdl(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["SDL"]["amount"], 35000)
		self.assertTrue(result["SDL"]["is_employer_only"])

	def test_wcf(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["WCF"]["amount"], 5000)
		self.assertTrue(result["WCF"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["NSSF Employee TZ"]["amount"], 0)
		self.assertEqual(result["NSSF Employer TZ"]["amount"], 0)
		self.assertEqual(result["SDL"]["amount"], 0)
		self.assertEqual(result["WCF"]["amount"], 0)


if __name__ == "__main__":
	unittest.main()
