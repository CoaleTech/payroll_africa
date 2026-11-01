"""Regression tests for LesothoCalculator.

LRA PAYE schedule:
  Annual 0 – 74,040 LSL : 20%
  Annual 74,040+ LSL    : 30%
  Annual tax credit     : 11,640 LSL (settable via tax_credit_annual)
  Optional zero-rate threshold (tax_free_threshold, annual LSL)
"""
import unittest
from unittest.mock import MagicMock

import sys
sys.modules["frappe"] = MagicMock()
sys.modules["frappe.utils"] = MagicMock()


def mock_flt(value, precision=None):
	if value is None:
		return 0.0
	try:
		return float(value)
	except (TypeError, ValueError):
		return 0.0


sys.modules["frappe.utils"].flt = mock_flt

from payroll_africa.calculators.lesotho import LesothoCalculator


def make_settings(tax_free_threshold=None, tax_credit_annual=11640):
	settings = MagicMock()
	settings.tax_free_threshold = tax_free_threshold
	settings.tax_credit_annual = tax_credit_annual
	return settings


def make_slip(gross):
	slip = MagicMock()
	slip.gross_pay = gross
	slip.earnings = []
	return slip


class TestLesothoPAYE(unittest.TestCase):

	def setUp(self):
		self.calc = LesothoCalculator(make_settings())

	def test_zero_gross(self):
		"""PAYE = 0 when gross = 0."""
		self.assertEqual(self.calc._compute_paye(0), 0)

	def test_band1(self):
		"""Annual 60,000 (gross 5,000/month): 60,000×20%−11,640 = 360 / 12 = 30."""
		paye = self.calc._compute_paye(5000)
		expected = (60000 * 0.20 - 11640) / 12
		self.assertAlmostEqual(paye, expected, places=2)

	def test_band2(self):
		"""Annual 120,000 (gross 10,000/month): 14,808+(120,000-74,040)×30%−11,640 = 16,956 / 12."""
		paye = self.calc._compute_paye(10000)
		raw = 14808 + (120000 - 74040) * 0.30
		expected = (raw - 11640) / 12
		self.assertAlmostEqual(paye, expected, places=2)

	def test_credit_absorbs_low_income(self):
		"""Annual 48,000 (gross 4,000/month): 48,000×20%−11,640 = −2,040 → capped at 0."""
		paye = self.calc._compute_paye(4000)
		self.assertEqual(paye, 0)

	def test_tax_free_threshold_zero_rate(self):
		"""If annual income ≤ tax_free_threshold setting, PAYE must be 0."""
		calc = LesothoCalculator(make_settings(tax_free_threshold=72000))
		# Gross 5,500/month → annual 66,000 ≤ 72,000 threshold
		self.assertEqual(calc._compute_paye(5500), 0)

	def test_tax_free_threshold_not_triggered_above(self):
		"""Annual income above threshold must still be taxed normally."""
		calc = LesothoCalculator(make_settings(tax_free_threshold=21600))
		# Gross 5,000/month → annual 60,000 > 21,600 → normal tax applies
		paye = calc._compute_paye(5000)
		self.assertGreater(paye, 0)

	def test_threshold_none_does_not_zero_tax(self):
		"""When tax_free_threshold is None (not configured), normal tax applies."""
		# Default settings has tax_free_threshold=None
		paye = self.calc._compute_paye(5000)
		self.assertGreater(paye, 0)

	def test_only_paye_component(self):
		"""Lesotho result dict should only contain PAYE."""
		result = self.calc.compute(make_slip(10000))
		self.assertIn("PAYE", result)
		self.assertEqual(len(result), 1)
		self.assertFalse(result["PAYE"]["is_employer_only"])

	def test_zero_gross_no_paye_key(self):
		"""Gross 0 → PAYE not included in results (amount 0 is omitted)."""
		result = self.calc.compute(make_slip(0))
		self.assertNotIn("PAYE", result)


if __name__ == "__main__":
	unittest.main()
