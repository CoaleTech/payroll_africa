"""Tests for Uganda statutory deduction calculator.

Band off-by-one regression: URA PAYE bands store from_amount = previous to_amount + 1.
The calculator adjusts floor = max(from_amount - 1, 0) so no shilling of width is lost.
"""
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
		self.assertAlmostEqual(result["LST"]["amount"], 100000 / 12, delta=0.01)
		self.assertFalse(result["LST"]["is_employer_only"])

	def test_zero_gross(self):
		result = self.calculator.compute(self._make_slip(0))
		self.assertEqual(result["NSSF Employee UG"]["amount"], 0)
		self.assertEqual(result["NSSF Employer UG"]["amount"], 0)
		# LST is still charged even with zero gross (flat tax)
		self.assertAlmostEqual(result["LST"]["amount"], 100000 / 12, delta=0.01)

	def test_nssf_rates_proportional(self):
		"""Employer NSSF should be double the employee NSSF (10% vs 5%)."""
		result = self.calculator.compute(self._make_slip(500000))
		self.assertAlmostEqual(
			result["NSSF Employer UG"]["amount"],
			result["NSSF Employee UG"]["amount"] * 2,
		)


def _make_paye_band(from_amount, to_amount, rate):
	b = MagicMock()
	b.from_amount = from_amount
	b.to_amount = to_amount
	b.rate = rate
	return b


class TestUgandaPAYE(unittest.TestCase):
	"""Regression tests for PAYE band off-by-one fix."""

	def _make_calc(self):
		settings = MagicMock()
		settings.nssf_employee_rate = 5
		settings.nssf_employer_rate = 10
		settings.lst_annual_amount = 0
		settings.lst_bands = []
		# URA PAYE monthly bands (2025)
		settings.paye_bands = [
			_make_paye_band(0,          235000,      0),
			_make_paye_band(235001,     335000,      10),
			_make_paye_band(335001,     410000,      20),
			_make_paye_band(410001,     10000000,    30),
			_make_paye_band(10000001,   0,           40),
		]
		return UgandaCalculator(settings)

	def _make_slip(self, gross):
		slip = MagicMock()
		slip.gross_pay = gross
		slip.earnings = [MagicMock(salary_component="Basic Salary", amount=gross)]
		return slip

	def test_paye_within_zero_band(self):
		"""Gross 200,000 UGX: all taxable income in 0% band — PAYE = 0."""
		# NSSF: 200000 * 5% = 10000; taxable = 190000 < 235000
		calc = self._make_calc()
		result = calc.compute(self._make_slip(200000))
		self.assertEqual(round(result["PAYE UG"]["amount"], 2), 0.0)

	def test_paye_boundary_regression(self):
		"""Gross 1,000,000 UGX: verifies floor adjustment at each band boundary.

		Without fix (floor=lower): PAYE = 186999.4
		With fix (floor=lower-1):  PAYE = 187000.0
		"""
		# NSSF: 1000000 * 5% = 50000; taxable = 950000
		# Band 0-235000:      floor=0,      in_band=235000, tax=0
		# Band 235001-335000: floor=235000, in_band=100000, tax=10000
		# Band 335001-410000: floor=335000, in_band=75000,  tax=15000
		# Band 410001-10M:    floor=410000, in_band=540000, tax=162000
		# PAYE = 187000
		calc = self._make_calc()
		result = calc.compute(self._make_slip(1000000))
		self.assertEqual(round(result["PAYE UG"]["amount"], 2), 187000.0)

	def test_paye_not_employer_only(self):
		"""PAYE UG is an employee deduction."""
		calc = self._make_calc()
		result = calc.compute(self._make_slip(500000))
		self.assertFalse(result["PAYE UG"]["is_employer_only"])


if __name__ == "__main__":
	unittest.main()
