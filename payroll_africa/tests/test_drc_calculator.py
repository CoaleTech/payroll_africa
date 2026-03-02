import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.drc import DRCCalculator


class TestDRCCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.inss_pension_employee_rate = 5
		self.settings.inss_pension_employer_rate = 5
		self.settings.inss_occupational_risks_rate = 1.5
		self.settings.inss_family_benefits_rate = 6.5
		self.settings.inpp_rate = 3
		self.settings.onem_rate = 0.2
		self.calculator = DRCCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_inss_pension_employee(self):
		result = self.calculator.compute(self._make_slip(2000000))
		self.assertAlmostEqual(result["INSS Pension Employee CD"]["amount"], 100000)
		self.assertFalse(result["INSS Pension Employee CD"]["is_employer_only"])

	def test_inss_pension_employer(self):
		result = self.calculator.compute(self._make_slip(2000000))
		self.assertAlmostEqual(result["INSS Pension Employer CD"]["amount"], 100000)
		self.assertTrue(result["INSS Pension Employer CD"]["is_employer_only"])

	def test_inss_occupational_risks(self):
		result = self.calculator.compute(self._make_slip(2000000))
		self.assertAlmostEqual(result["INSS Occupational Risks CD"]["amount"], 30000)
		self.assertTrue(result["INSS Occupational Risks CD"]["is_employer_only"])

	def test_inss_family_benefits(self):
		result = self.calculator.compute(self._make_slip(2000000))
		self.assertAlmostEqual(result["INSS Family Benefits CD"]["amount"], 130000)
		self.assertTrue(result["INSS Family Benefits CD"]["is_employer_only"])

	def test_inpp(self):
		result = self.calculator.compute(self._make_slip(2000000))
		self.assertAlmostEqual(result["INPP CD"]["amount"], 60000)
		self.assertTrue(result["INPP CD"]["is_employer_only"])

	def test_onem(self):
		result = self.calculator.compute(self._make_slip(2000000))
		self.assertAlmostEqual(result["ONEM CD"]["amount"], 4000)
		self.assertTrue(result["ONEM CD"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["INSS Pension Employee CD"]["amount"], 0)
		self.assertEqual(result["INSS Pension Employer CD"]["amount"], 0)
		self.assertEqual(result["INSS Occupational Risks CD"]["amount"], 0)
		self.assertEqual(result["INSS Family Benefits CD"]["amount"], 0)
		self.assertEqual(result["INPP CD"]["amount"], 0)
		self.assertEqual(result["ONEM CD"]["amount"], 0)

	def test_all_components_returned(self):
		result = self.calculator.compute(self._make_slip(2000000))
		self.assertEqual(len(result), 6)


if __name__ == "__main__":
	unittest.main()
