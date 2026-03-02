import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.burundi import BurundiCalculator


class TestBurundiCalculator(unittest.TestCase):
	def setUp(self):
		self.settings = MagicMock()
		self.settings.inss_employee_rate = 4
		self.settings.inss_employer_rate = 6
		self.settings.work_injury_rate = 3
		self.settings.health_employee_rate = 3
		self.settings.health_employer_rate = 3
		self.settings.training_employee_rate = 1
		self.settings.training_employer_rate = 1
		self.calculator = BurundiCalculator(self.settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_inss_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["INSS Employee BI"]["amount"], 40000)
		self.assertFalse(result["INSS Employee BI"]["is_employer_only"])

	def test_inss_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["INSS Employer BI"]["amount"], 60000)
		self.assertTrue(result["INSS Employer BI"]["is_employer_only"])

	def test_work_injury(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Work Injury BI"]["amount"], 30000)
		self.assertTrue(result["Work Injury BI"]["is_employer_only"])

	def test_health_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Health Insurance Employee BI"]["amount"], 30000)
		self.assertFalse(result["Health Insurance Employee BI"]["is_employer_only"])

	def test_health_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Health Insurance Employer BI"]["amount"], 30000)
		self.assertTrue(result["Health Insurance Employer BI"]["is_employer_only"])

	def test_training_employee(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Training Fund Employee BI"]["amount"], 10000)
		self.assertFalse(result["Training Fund Employee BI"]["is_employer_only"])

	def test_training_employer(self):
		result = self.calculator.compute(self._make_slip(1000000))
		self.assertAlmostEqual(result["Training Fund Employer BI"]["amount"], 10000)
		self.assertTrue(result["Training Fund Employer BI"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["INSS Employee BI"]["amount"], 0)
		self.assertEqual(result["INSS Employer BI"]["amount"], 0)
		self.assertEqual(result["Work Injury BI"]["amount"], 0)
		self.assertEqual(result["Health Insurance Employee BI"]["amount"], 0)
		self.assertEqual(result["Health Insurance Employer BI"]["amount"], 0)
		self.assertEqual(result["Training Fund Employee BI"]["amount"], 0)
		self.assertEqual(result["Training Fund Employer BI"]["amount"], 0)

	def test_all_components_returned(self):
		"""All 7 statutory components should be present."""
		result = self.calculator.compute(self._make_slip(500000))
		expected_keys = [
			"INSS Employee BI",
			"INSS Employer BI",
			"Work Injury BI",
			"Health Insurance Employee BI",
			"Health Insurance Employer BI",
			"Training Fund Employee BI",
			"Training Fund Employer BI",
		]
		for key in expected_keys:
			self.assertIn(key, result)


if __name__ == "__main__":
	unittest.main()
