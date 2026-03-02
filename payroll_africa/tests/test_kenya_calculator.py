import unittest
from unittest.mock import MagicMock

from payroll_africa.calculators.kenya import KenyaCalculator


def make_settings():
	"""Create mock Kenya Payroll Settings with 2025 rates."""
	settings = MagicMock()
	settings.shif_rate = 2.75
	settings.shif_minimum = 300
	settings.ahl_employee_rate = 1.5
	settings.ahl_employer_rate = 1.5
	settings.nssf_tier1_rate = 6
	settings.nssf_tier1_cap = 1080
	settings.nssf_tier1_upper_limit = 18000
	settings.nssf_tier2_rate = 6
	settings.nssf_tier2_cap = 1080
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

	def test_nssf_below_tier1_limit(self):
		"""Gross 15,000 - below Tier I upper limit, no Tier II."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		# Tier I: 15000 * 6% = 900 (below cap of 1080)
		self.assertEqual(get_amount(results, "NSSF Employee"), 900.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 900.0)
		self.assertFalse(results["NSSF Employee"]["is_employer_only"])
		self.assertTrue(results["NSSF Employer"]["is_employer_only"])

	def test_nssf_at_tier1_cap(self):
		"""Gross 18,000 - exactly at Tier I upper limit."""
		slip = make_salary_slip(18000)
		results = self.calculator.compute(slip)

		# Tier I: 18000 * 6% = 1080 (at cap)
		# Tier II: (18000 - 18000) * 6% = 0
		self.assertEqual(get_amount(results, "NSSF Employee"), 1080.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 1080.0)

	def test_nssf_with_tier2(self):
		"""Gross 30,000 - triggers Tier II."""
		slip = make_salary_slip(30000)
		results = self.calculator.compute(slip)

		# Tier I: 30000 * 6% = 1800, capped at 1080
		# Tier II: (30000 - 18000) * 6% = 720 (below cap of 1080)
		self.assertEqual(get_amount(results, "NSSF Employee"), 1800.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 1800.0)

	def test_nssf_both_tiers_capped(self):
		"""Gross 50,000 - both tiers hit their caps."""
		slip = make_salary_slip(50000)
		results = self.calculator.compute(slip)

		# Tier I: 50000 * 6% = 3000, capped at 1080
		# Tier II: (50000 - 18000) * 6% = 1920, capped at 1080
		self.assertEqual(get_amount(results, "NSSF Employee"), 2160.0)
		self.assertEqual(get_amount(results, "NSSF Employer"), 2160.0)

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

		# NSSF: Tier I cap 1080 + Tier II (50000-18000)*6%=1920 capped at 1080 = 2160
		self.assertEqual(get_amount(results, "NSSF Employee"), 2160.0)

		# SHIF: 50000 * 2.75% = 1375
		self.assertEqual(get_amount(results, "SHIF"), 1375.0)

		# Housing Levy: 50000 * 1.5% = 750
		self.assertEqual(get_amount(results, "Housing Levy"), 750.0)
		self.assertEqual(get_amount(results, "Employer Housing Levy"), 750.0)

		# NITA: 50
		self.assertEqual(get_amount(results, "NITA"), 50.0)

		# Total employee deductions (before PAYE): 2160 + 1375 + 750 = 4285
		employee_deductions = sum(
			v["amount"] for k, v in results.items() if not v["is_employer_only"]
		)
		self.assertEqual(round(employee_deductions, 2), 4285.0)

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
