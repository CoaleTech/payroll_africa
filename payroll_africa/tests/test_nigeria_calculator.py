import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.nigeria import NigeriaCalculator


class TestNigeriaCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.pension_employee_rate = 8
		self.settings.pension_employer_rate = 10
		self.settings.nhf_rate = 2.5
		self.settings.nhis_employee_rate = 5
		self.settings.nhis_employer_rate = 10
		self.settings.nsitf_rate = 1
		self.settings.itf_rate = 1
		self.calculator = NigeriaCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_pension_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Pension Employee NG"]["amount"], 80000)  # 1000000 * 8%
		self.assertFalse(result["Pension Employee NG"]["is_employer_only"])

	def test_pension_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Pension Employer NG"]["amount"], 100000)  # 1000000 * 10%
		self.assertTrue(result["Pension Employer NG"]["is_employer_only"])

	def test_nhf(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NHF NG"]["amount"], 25000)  # 1000000 * 2.5%
		self.assertFalse(result["NHF NG"]["is_employer_only"])

	def test_nhis_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NHIS Employee NG"]["amount"], 50000)  # 1000000 * 5%
		self.assertFalse(result["NHIS Employee NG"]["is_employer_only"])

	def test_nhis_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NHIS Employer NG"]["amount"], 100000)  # 1000000 * 10%
		self.assertTrue(result["NHIS Employer NG"]["is_employer_only"])

	def test_nsitf(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["NSITF NG"]["amount"], 10000)  # 1000000 * 1%
		self.assertTrue(result["NSITF NG"]["is_employer_only"])

	def test_itf(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["ITF NG"]["amount"], 10000)  # 1000000 * 1%
		self.assertTrue(result["ITF NG"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["Pension Employee NG"]["amount"], 0)
		self.assertEqual(result["Pension Employer NG"]["amount"], 0)
		self.assertEqual(result["NHF NG"]["amount"], 0)
		self.assertEqual(result["NHIS Employee NG"]["amount"], 0)
		self.assertEqual(result["NHIS Employer NG"]["amount"], 0)
		self.assertEqual(result["NSITF NG"]["amount"], 0)
		self.assertEqual(result["ITF NG"]["amount"], 0)

	def test_all_components_returned(self):
		result = self.calculator.compute(self._make_slip(1000000))
		expected = {
			"Pension Employee NG", "Pension Employer NG",
			"NHF NG",
			"NHIS Employee NG", "NHIS Employer NG",
			"NSITF NG", "ITF NG",
		}
		self.assertEqual(set(result.keys()), expected)


if __name__ == "__main__":
	unittest.main()
