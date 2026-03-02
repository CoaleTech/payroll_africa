import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.rwanda import RwandaCalculator


class TestRwandaCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.pension_employee_rate = 6
		self.settings.pension_employer_rate = 6
		self.settings.maternity_employee_rate = 0.3
		self.settings.maternity_employer_rate = 0.3
		self.settings.cbhi_rate = 0.5
		self.settings.occupational_hazards_rate = 2
		self.calculator = RwandaCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_pension_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Pension Employee RW"]["amount"], 60000)
		self.assertFalse(result["Pension Employee RW"]["is_employer_only"])

	def test_pension_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Pension Employer RW"]["amount"], 60000)
		self.assertTrue(result["Pension Employer RW"]["is_employer_only"])

	def test_maternity_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Maternity Employee RW"]["amount"], 3000)
		self.assertFalse(result["Maternity Employee RW"]["is_employer_only"])

	def test_maternity_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Maternity Employer RW"]["amount"], 3000)
		self.assertTrue(result["Maternity Employer RW"]["is_employer_only"])

	def test_cbhi(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["CBHI RW"]["amount"], 5000)
		self.assertFalse(result["CBHI RW"]["is_employer_only"])

	def test_occupational_hazards(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Occupational Hazards RW"]["amount"], 20000)
		self.assertTrue(result["Occupational Hazards RW"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["Pension Employee RW"]["amount"], 0)
		self.assertEqual(result["Pension Employer RW"]["amount"], 0)
		self.assertEqual(result["Maternity Employee RW"]["amount"], 0)
		self.assertEqual(result["Maternity Employer RW"]["amount"], 0)
		self.assertEqual(result["CBHI RW"]["amount"], 0)
		self.assertEqual(result["Occupational Hazards RW"]["amount"], 0)


if __name__ == "__main__":
	unittest.main()
