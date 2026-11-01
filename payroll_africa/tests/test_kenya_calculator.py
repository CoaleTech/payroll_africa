import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.kenya import KenyaCalculator


def make_band(from_amount, to_amount, rate):
	"""Create a mock PAYE/NSSF band row."""
	b = MagicMock()
	b.from_amount = from_amount
	b.to_amount = to_amount
	b.rate = rate
	return b


def make_settings():
	"""Create mock Kenya Payroll Settings (SHIF/AHL/PAYE 2025; NSSF Year 4, Feb 2026)."""
	settings = MagicMock()
	settings.shif_rate = 2.75
	settings.shif_minimum = 300
	settings.ahl_employee_rate = 1.5
	settings.ahl_employer_rate = 1.5
	settings.nssf_tier1_rate = 6
	settings.nssf_tier1_cap = 540
	settings.nssf_tier1_upper_limit = 9000
	settings.nssf_tier2_rate = 6
	settings.nssf_tier2_cap = 5940
	settings.nita_amount = 50
	settings.personal_relief = 2400
	# KRA PAYE monthly bands (calculator uses monthly gross)
	settings.paye_bands = [
		make_band(0,      24000,   10),
		make_band(24001,  32333,   25),
		make_band(32334,  500000,  30),
		make_band(500001, 800000,  32.5),
		make_band(800001, 0,       35),
	]
	return settings


def make_salary_slip(gross_pay, basic_pay=None):
	"""Create mock Salary Slip."""
	slip = MagicMock()
	slip.gross_pay = gross_pay
	slip.earnings = []
	if basic_pay is not None:
		earning = MagicMock()
		earning.salary_component = "Basic Salary"
		earning.amount = basic_pay
		slip.earnings.append(earning)
	return slip


def get_amount(results, key):
	return round(results[key]["amount"], 2)


class TestKenyaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = KenyaCalculator(self.settings)

	def test_nssf_tier1_only(self):
		"""Gross 9,000 - all within Tier I (LEL)."""
		slip = make_salary_slip(9000)
		results = self.calculator.compute(slip)

		# Tier I: 9000 * 6% = 540 (at cap); Tier II: 0
		self.assertEqual(get_amount(results, "NSSF Employee"), 540.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 540.0)
		self.assertFalse(results["NSSF Employee"]["is_employer_only"])
		self.assertTrue(results["NSSF Employer"]["is_employer_only"])

	def test_nssf_with_tier2(self):
		"""Gross 30,000 - Tier I capped + partial Tier II."""
		slip = make_salary_slip(30000)
		results = self.calculator.compute(slip)

		# Tier I: 540 (cap); Tier II: (30000 - 9000) * 6% = 1260 (below cap 5940)
		self.assertEqual(get_amount(results, "NSSF Employee"), 1800.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 1800.0)

	def test_nssf_mid_band(self):
		"""Gross 50,000 - Tier II accruing, below its cap."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)

		# Tier I: 540 (cap); Tier II: (50000 - 9000) * 6% = 2460 (below cap 5940)
		self.assertEqual(get_amount(results, "NSSF Employee"), 3000.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 3000.0)

	def test_nssf_both_tiers_capped(self):
		"""Gross 150,000 - both tiers at their caps (max NSSF 6,480)."""
		slip = make_salary_slip(150000)
		results = self.calculator.compute(slip)

		# Tier I: 540 (cap); Tier II: capped at 5940 -> total 6480
		self.assertEqual(get_amount(results, "NSSF Employee"), 6480.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 6480.0)

	def test_shif_normal(self):
		"""SHIF at 2.75% of gross."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)

		# 50000 * 2.75% = 1375
		self.assertEqual(get_amount(results, "SHIF"), 1375.0)
		self.assertFalse(results["SHIF"]["is_employer_only"])

	def test_shif_minimum(self):
		"""SHIF should not go below minimum."""
		slip = make_salary_slip(5000)
		results = self.calculator.compute(slip)

		# 5000 * 2.75% = 137.5, but minimum is 300
		self.assertEqual(get_amount(results, "SHIF"), 300.0)

	def test_shif_zero_gross(self):
		"""SHIF should be 0 when gross is 0."""
		slip = make_salary_slip(0)
		results = self.calculator.compute(slip)
		self.assertEqual(get_amount(results, "SHIF"), 0.0)

	def test_housing_levy(self):
		"""Housing Levy at 1.5% each for employee and employer."""
		slip = make_salary_slip(100000)
		results = self.calculator.compute(slip)

		# 100000 * 1.5% = 1500
		self.assertEqual(get_amount(results, "Housing Levy"), 1500.0)
		self.assertEqual(get_amount(results, "Employer Housing Levy"), 1500.0)
		self.assertFalse(results["Housing Levy"]["is_employer_only"])
		self.assertTrue(results["Employer Housing Levy"]["is_employer_only"])

	def test_nita(self):
		"""NITA is flat KES 50 employer-only."""
		slip = make_salary_slip(100000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "NITA"), 50.0)
		self.assertTrue(results["NITA"]["is_employer_only"])

	def test_full_computation_50k(self):
		"""Full computation for KES 50,000 gross — employee totals exclude PAYE."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)

		# NSSF: Tier I 540 (cap) + Tier II (50000-9000)*6%=2460 = 3000
		self.assertEqual(get_amount(results, "NSSF Employee"), 3000.0)

		# SHIF: 50000 * 2.75% = 1375
		self.assertEqual(get_amount(results, "SHIF"), 1375.0)

		# Housing Levy: 50000 * 1.5% = 750
		self.assertEqual(get_amount(results, "Housing Levy"), 750.0)
		self.assertEqual(get_amount(results, "Employer Housing Levy"), 750.0)

		# NITA: 50
		self.assertEqual(get_amount(results, "NITA"), 50.0)

		# Non-PAYE employee deductions: NSSF(3000) + SHIF(1375) + AHL(750) = 5125
		non_paye_employee = sum(
			v["amount"] for k, v in results.items()
			if not v["is_employer_only"] and k != "PAYE"
		)
		self.assertEqual(round(non_paye_employee, 2), 5125.0)

	def test_paye_computed(self):
		"""PAYE should be in results (calculator overrides HRMS slab)."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)
		self.assertIn("PAYE", results)
		self.assertFalse(results["PAYE"]["is_employer_only"])

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)

		expected = {
			"NSSF Employee", "NSSF Employer", "SHIF",
			"Housing Levy", "Employer Housing Levy", "NITA", "PAYE",
		}
		self.assertEqual(set(results.keys()), expected)

	def test_paye_zero_below_personal_relief(self):
		"""Gross 25,000: tax before relief < 2,400 so PAYE = 0."""
		# NSSF: Tier I=540 + Tier II=(25000-9000)*6%=960 = 1500
		# taxable = 25000 - 1500 = 23500
		# Band 0-24000: 23500 * 10% = 2350 < personal_relief 2400 => PAYE = 0
		slip = make_salary_slip(25000)
		results = self.calculator.compute(slip)
		self.assertEqual(get_amount(results, "PAYE"), 0.0)

	def test_paye_amount_30k(self):
		"""Gross 30,000: spot-check PAYE calculation with personal relief.

		allowable = NSSF(1800) + SHIF(825) + AHL(450) = 3,075
		taxable = 30,000 - 3,075 = 26,925
		Band 0-24000:    24000 * 10% = 2,400
		Band 24001-32333: 2925 * 25% =   731.25
		Tax before relief = 3,131.25; after 2,400 relief => PAYE = 731.25
		"""
		slip = make_salary_slip(30000)
		results = self.calculator.compute(slip)
		self.assertEqual(get_amount(results, "PAYE"), 731.25)

	def test_paye_amount_50k(self):
		"""Gross 50,000: PAYE spans three bands.

		allowable = NSSF(3000) + SHIF(1375) + AHL(750) = 5,125
		taxable = 50,000 - 5,125 = 44,875
		Band 0-24000:      24000 * 10%  = 2,400.00
		Band 24001-32333:   8333 * 25%  = 2,083.25
		Band 32334-500000: 12542 * 30%  = 3,762.60
		Tax before relief = 8,245.85; after 2,400 relief => PAYE = 5,845.85
		"""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)
		self.assertEqual(get_amount(results, "PAYE"), 5845.85)


if __name__ == "__main__":
	unittest.main()
