"""Regression tests for ZimbabweCalculator.

Covers NSSA ceiling, AIDS levy, and PAYE formula-method with band-based
and hardcoded paths.  All calculations in USD (currency_mode="USD").

ZIMRA formula method (monthly USD):
  0 – 100     : 0%  − 0
  101 – 300   : 20% − 20
  301 – 1,000 : 25% − 35
  1,001 – 2,000: 30% − 85
  2,001 – 3,000: 35% − 185
  3,001+       : 40% − 335
"""
import unittest
from types import SimpleNamespace
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

from payroll_africa.calculators.zimbabwe import ZimbabweCalculator


def make_settings(paye_bands=None):
	"""Return minimal Zimbabwe Payroll Settings mock (USD mode)."""
	settings = MagicMock()
	settings.currency_mode = "USD"
	settings.tax_free_threshold = 100
	settings.nssa_rate = 4.5
	settings.nssa_annual_ceiling = 8400    # USD 700/month × 12 (2025)
	settings.aids_levy_rate = 3
	settings.paye_bands = paye_bands or []
	settings.get = lambda k, d=None: getattr(settings, k, d)
	return settings


def make_slip(gross):
	slip = MagicMock()
	slip.gross_pay = gross
	slip.earnings = []
	return slip


def make_bands():
	"""ZIMRA 2025 monthly USD formula bands."""
	return [
		SimpleNamespace(from_amount=0,    to_amount=100,  rate=0,  deduction=0),
		SimpleNamespace(from_amount=101,  to_amount=300,  rate=20, deduction=20),
		SimpleNamespace(from_amount=301,  to_amount=1000, rate=25, deduction=35),
		SimpleNamespace(from_amount=1001, to_amount=2000, rate=30, deduction=85),
		SimpleNamespace(from_amount=2001, to_amount=3000, rate=35, deduction=185),
		SimpleNamespace(from_amount=3001, to_amount=0,    rate=40, deduction=335),
	]


class TestZimbabweNSSA(unittest.TestCase):
	"""NSSA ceiling must use 8,400/year (USD 700/month), not 1,914,360 (old ZiG value)."""

	def setUp(self):
		self.calc = ZimbabweCalculator(make_settings())

	def test_nssa_below_ceiling(self):
		"""Gross 500 < 700 ceiling → NSSA = 500 × 4.5% = 22.50."""
		result = self.calc._compute_nssa(500)
		self.assertAlmostEqual(result, 500 * 0.045, places=2)

	def test_nssa_at_ceiling(self):
		"""Gross 700 = monthly ceiling → NSSA = 700 × 4.5% = 31.50."""
		result = self.calc._compute_nssa(700)
		self.assertAlmostEqual(result, 700 * 0.045, places=2)

	def test_nssa_above_ceiling(self):
		"""Gross 2,000 > USD 700 ceiling → NSSA capped at 700 × 4.5% = 31.50."""
		result = self.calc._compute_nssa(2000)
		self.assertAlmostEqual(result, 700 * 0.045, places=2)

	def test_nssa_ceiling_not_zig(self):
		"""Regression: old ZiG ceiling 1,914,360/year = 159,530/month caused no cap.
		At USD 2,000 gross the ZiG path would give 2,000 × 4.5% = 90; correct is 31.50."""
		result = self.calc._compute_nssa(2000)
		self.assertAlmostEqual(result, 31.5, places=2)
		self.assertNotAlmostEqual(result, 90, places=1)


class TestZimbabwePAYEHardcoded(unittest.TestCase):
	"""_paye_hardcoded fallback: ZIMRA formula tax = gross × rate − deduction."""

	def setUp(self):
		self.calc = ZimbabweCalculator(make_settings())

	def test_below_threshold(self):
		self.assertAlmostEqual(self.calc._paye_hardcoded(80), 0, places=2)

	def test_band2_midpoint(self):
		"""200 USD: 200 × 20% − 20 = 20."""
		self.assertAlmostEqual(self.calc._paye_hardcoded(200), 20, places=2)

	def test_band3_midpoint(self):
		"""650 USD: 650 × 25% − 35 = 127.50."""
		self.assertAlmostEqual(self.calc._paye_hardcoded(650), 127.50, places=2)

	def test_band6_top(self):
		"""5,000 USD: 5,000 × 40% − 335 = 1,665."""
		self.assertAlmostEqual(self.calc._paye_hardcoded(5000), 1665, places=2)


class TestZimbabwePAYEBands(unittest.TestCase):
	"""_compute_paye with DB bands (formula method via paye_bands)."""

	def setUp(self):
		self.calc = ZimbabweCalculator(make_settings(paye_bands=make_bands()))

	def test_band2(self):
		"""200 USD → band 2: 200 × 20% − 20 = 20."""
		self.assertAlmostEqual(self.calc._compute_paye(200), 20, places=2)

	def test_band3(self):
		"""650 USD → band 3: 650 × 25% − 35 = 127.50."""
		self.assertAlmostEqual(self.calc._compute_paye(650), 127.50, places=2)

	def test_band5(self):
		"""2,500 USD → band 5: 2,500 × 35% − 185 = 690."""
		self.assertAlmostEqual(self.calc._compute_paye(2500), 690, places=2)

	def test_below_threshold(self):
		"""80 USD ≤ threshold 100 → PAYE = 0."""
		self.assertAlmostEqual(self.calc._compute_paye(80), 0, places=2)


class TestZimbabweAIDSLevy(unittest.TestCase):
	"""AIDS levy = 3% of PAYE (after PAYE is computed)."""

	def setUp(self):
		self.calc = ZimbabweCalculator(make_settings(paye_bands=make_bands()))

	def test_aids_levy_on_positive_paye(self):
		"""AIDS levy = 3% of PAYE; PAYE is computed on gross − NSSA (not gross directly).

		gross=650, NSSA=650×4.5%=29.25, taxable=620.75
		PAYE=620.75×25%−35=120.1875 (band 3)
		AIDS levy=120.1875×3%=3.605625
		"""
		gross = 650
		nssa = gross * 0.045                     # 29.25 (below 700 ceiling)
		taxable = gross - nssa                   # 620.75
		expected_paye = taxable * 0.25 - 35      # 120.1875
		expected_aids = expected_paye * 0.03     # 3.605625

		result = self.calc.compute(make_slip(gross))
		self.assertIn("AIDS Levy", result)
		self.assertAlmostEqual(result["AIDS Levy"]["amount"], expected_aids, places=4)
		self.assertFalse(result["AIDS Levy"]["is_employer_only"])

	def test_aids_levy_is_3pct_of_paye(self):
		"""Ratio of AIDS Levy to PAYE must equal aids_levy_rate / 100."""
		result = self.calc.compute(make_slip(1500))
		self.assertIn("PAYE", result)
		self.assertIn("AIDS Levy", result)
		ratio = result["AIDS Levy"]["amount"] / result["PAYE"]["amount"]
		self.assertAlmostEqual(ratio, 0.03, places=6)

if __name__ == "__main__":
	unittest.main()
