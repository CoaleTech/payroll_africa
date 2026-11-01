import unittest
from unittest.mock import MagicMock

# Mock frappe before importing calculators
import sys
sys.modules["frappe"] = MagicMock()
sys.modules["frappe.utils"] = MagicMock()


def mock_flt(value, precision=None):
	if value is None:
		return 0.0
	return float(value)


sys.modules["frappe.utils"].flt = mock_flt

from payroll_africa.calculators.namibia import NamibiaCalculator


def make_settings():
	"""Create mock Namibia Payroll Settings with 2025/2026 rates."""
	settings = MagicMock()
	settings.ssc_annual_ceiling = 150000
	settings.ssc_rate = 0.9
	settings.vet_levy_applicable = 1
	settings.vet_levy_rate = 1
	settings.ecf_risk_sector = "low"
	settings.paye_bands = []
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


class TestNamibiaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = NamibiaCalculator(self.settings)

	def test_ssc_capped(self):
		"""SSC capped at NAD 150,000/year (N$12,500/month, from 1 Sep 2026)."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		# 0.9% of 12,500 (monthly cap) = 112.50
		self.assertEqual(get_amount(results, "Social Security Employee"), 112.50)
		self.assertEqual(get_amount(results, "Social Security Employer"), 112.50)
		self.assertFalse(results["Social Security Employee"]["is_employer_only"])
		self.assertTrue(results["Social Security Employer"]["is_employer_only"])

	def test_ssc_below_cap(self):
		"""SSC below ceiling: 0.9% of gross."""
		slip = make_salary_slip(5000)
		results = self.calculator.compute(slip)

		# 0.9% of 5,000 = 45
		self.assertEqual(get_amount(results, "Social Security Employee"), 45.0)

	def test_vet_levy(self):
		"""VET levy: 1% of gross, employer only."""
		slip = make_salary_slip(20000)
		results = self.calculator.compute(slip)

		# 1% of 20,000 = 200
		self.assertEqual(get_amount(results, "VET Levy"), 200.0)
		self.assertTrue(results["VET Levy"]["is_employer_only"])

	def test_ecf_by_risk(self):
		"""ECF for low risk sector: 1% of gross."""
		slip = make_salary_slip(20000)
		results = self.calculator.compute(slip)

		# Low risk: 1% of 20,000 = 200
		self.assertEqual(get_amount(results, "Employees Compensation"), 200.0)
		self.assertTrue(results["Employees Compensation"]["is_employer_only"])

	def test_paye_positive(self):
		"""PAYE should be positive for a mid-income salary."""
		slip = make_salary_slip(20000)
		results = self.calculator.compute(slip)

		paye = results["PAYE"]["amount"]
		self.assertGreater(paye, 0)
		self.assertFalse(results["PAYE"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "Social Security Employee"), 0.0)
		self.assertEqual(get_amount(results, "Social Security Employer"), 0.0)
		self.assertNotIn("VET Levy", results)
		self.assertNotIn("Employees Compensation", results)
		self.assertEqual(get_amount(results, "PAYE"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(20000)
		results = self.calculator.compute(slip)

		expected = {
			"Social Security Employee",
			"Social Security Employer",
			"VET Levy",
			"Employees Compensation",
			"PAYE",
		}
		self.assertEqual(set(results.keys()), expected)

	def test_paye_bands_formula(self):
		"""PAYE with 2025/26 bands: gross 25,000 → annual 300,000 → band 150k-350k@25%,base9k."""
		from types import SimpleNamespace
		self.settings.paye_bands = [
			SimpleNamespace(from_amount=0,       to_amount=100000,  rate=0,  base_tax=0),
			SimpleNamespace(from_amount=100001,  to_amount=150000,  rate=18, base_tax=0),
			SimpleNamespace(from_amount=150001,  to_amount=350000,  rate=25, base_tax=9000),
			SimpleNamespace(from_amount=350001,  to_amount=550000,  rate=28, base_tax=59000),
			SimpleNamespace(from_amount=550001,  to_amount=850000,  rate=30, base_tax=115000),
			SimpleNamespace(from_amount=850001,  to_amount=1550000, rate=32, base_tax=205000),
			SimpleNamespace(from_amount=1550001, to_amount=0,       rate=37, base_tax=429000),
		]
		# annual=300,000; band150k-350k: 9,000+(300,000-150,001)*25%=9,000+37,499.75=46,499.75
		# monthly=46,499.75/12≈3,874.98
		slip = make_salary_slip(25000)
		results = self.calculator.compute(slip)
		self.assertAlmostEqual(results["PAYE"]["amount"], 46499.75 / 12, places=1)

	def test_paye_bands_formula_not_accumulated(self):
		"""Regression: band formula must NOT accumulate base_tax across all bands."""
		from types import SimpleNamespace
		self.settings.paye_bands = [
			SimpleNamespace(from_amount=0,      to_amount=100000, rate=0,  base_tax=0),
			SimpleNamespace(from_amount=100001, to_amount=150000, rate=18, base_tax=0),
			SimpleNamespace(from_amount=150001, to_amount=0,      rate=25, base_tax=9000),
		]
		# Gross 25,000 → annual 300,000 → band 150k+: 9,000 + (300,000-150,001)×25%
		expected_annual = 9000 + (300000 - 150001) * 0.25  # 46,499.75
		slip = make_salary_slip(25000)
		results = self.calculator.compute(slip)
		self.assertAlmostEqual(results["PAYE"]["amount"], expected_annual / 12, places=1)
		# Accumulation bug would give much more; ensure well below that
		self.assertLess(results["PAYE"]["amount"], 60000 / 12)


if __name__ == "__main__":
	unittest.main()
