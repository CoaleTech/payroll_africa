import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.kenya import KenyaCalculator


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
		"""Full computation for KES 50,000 gross."""
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

		# Total employee deductions (before PAYE): 3000 + 1375 + 750 = 5125
		employee_deductions = sum(
			v["amount"] for k, v in results.items() if not v["is_employer_only"]
		)
		self.assertEqual(round(employee_deductions, 2), 5125.0)

	def test_paye_not_computed(self):
		"""PAYE should NOT be in results (handled by HRMS)."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)
		self.assertNotIn("PAYE", results)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)

		expected = {"NSSF Employee", "NSSF Employer", "SHIF", "Housing Levy", "Employer Housing Levy", "NITA"}
		self.assertEqual(set(results.keys()), expected)


if __name__ == "__main__":
	unittest.main()
