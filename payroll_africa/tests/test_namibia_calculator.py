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
	settings.ssc_annual_ceiling = 108000
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
		"""SSC capped at NAD 108,000/year = NAD 9,000/month."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		# 0.9% of 9,000 = 81
		self.assertEqual(get_amount(results, "Social Security Employee"), 81.0)
		self.assertEqual(get_amount(results, "Social Security Employer"), 81.0)
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


if __name__ == "__main__":
	unittest.main()
