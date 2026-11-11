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

# Prevent frappe.db.get_value from returning a truthy MagicMock in _get_employee_age
sys.modules["frappe"].db.get_value.return_value = None

from payroll_africa.calculators.south_africa import SouthAfricaCalculator


def make_settings():
	"""Create mock South Africa Payroll Settings with 2024/2025 rates."""
	settings = MagicMock()
	settings.uif_ceiling = 17712
	settings.uif_rate = 1
	settings.sdl_applicable = 1
	settings.sdl_rate = 1
	settings.rebate_primary = 17235
	settings.threshold_under_65 = 95750
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


class TestSouthAfricaCalculator(unittest.TestCase):

	def setUp(self):
		self.settings = make_settings()
		self.calculator = SouthAfricaCalculator(self.settings)

	def test_uif_capped(self):
		"""UIF capped at R17,712 x 1% = R177.12."""
		slip = make_salary_slip(25000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "UIF Employee"), 177.12)
		self.assertEqual(get_amount(results, "UIF Employer"), 177.12)
		self.assertFalse(results["UIF Employee"]["is_employer_only"])
		self.assertTrue(results["UIF Employer"]["is_employer_only"])

	def test_uif_below_cap(self):
		"""UIF below ceiling: 1% of gross."""
		slip = make_salary_slip(15000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "UIF Employee"), 150.0)
		self.assertEqual(get_amount(results, "UIF Employer"), 150.0)

	def test_sdl_applied(self):
		"""SDL is 1% of gross when applicable."""
		slip = make_salary_slip(20000)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "SDL"), 200.0)
		self.assertTrue(results["SDL"]["is_employer_only"])

	def test_paye_progressive(self):
		"""PAYE should be positive for a mid-income salary."""
		slip = make_salary_slip(30000)
		results = self.calculator.compute(slip)

		paye = results["PAYE"]["amount"]
		self.assertGreater(paye, 0)
		self.assertFalse(results["PAYE"]["is_employer_only"])

	def test_zero_salary(self):
		"""All deductions should be zero when gross is zero."""
		slip = make_salary_slip(0)
		results = self.calculator.compute(slip)

		self.assertEqual(get_amount(results, "UIF Employee"), 0.0)
		self.assertEqual(get_amount(results, "UIF Employer"), 0.0)
		self.assertNotIn("SDL", results)
		self.assertEqual(get_amount(results, "PAYE"), 0.0)

	def test_all_components_present(self):
		"""All expected components should be in results."""
		slip = make_salary_slip(30000)
		results = self.calculator.compute(slip)

		expected = {"UIF Employee", "UIF Employer", "SDL", "PAYE"}
		self.assertEqual(set(results.keys()), expected)

	def test_paye_formula_band1_boundary(self):
		"""Hardcoded: annual 237,100 → top of band 1 → 237,100 × 18% = 42,678."""
		raw = self.calculator._sars_tax_formula(237100)
		self.assertAlmostEqual(raw, 42678, places=0)

	def test_paye_formula_band3_boundary(self):
		"""Hardcoded: annual 512,800 → top of band 3 → 77,362 + 142,299 × 31% ≈ 121,475."""
		raw = self.calculator._sars_tax_formula(512800)
		self.assertAlmostEqual(raw, 121475, delta=1)

	def test_paye_bands_formula_not_accumulated(self):
		"""DB bands: base_tax applied once for matching band; no cross-band accumulation."""
		from types import SimpleNamespace
		self.settings.paye_bands = [
			SimpleNamespace(from_amount=0,       to_amount=237100,  base_tax=0,      rate=18),
			SimpleNamespace(from_amount=237101,  to_amount=370500,  base_tax=42678,  rate=26),
			SimpleNamespace(from_amount=370501,  to_amount=512800,  base_tax=77362,  rate=31),
			SimpleNamespace(from_amount=512801,  to_amount=673000,  base_tax=121475, rate=36),
			SimpleNamespace(from_amount=673001,  to_amount=857900,  base_tax=179147, rate=39),
			SimpleNamespace(from_amount=857901,  to_amount=1817000, base_tax=251258, rate=41),
			SimpleNamespace(from_amount=1817001, to_amount=0,       base_tax=644489, rate=45),
		]
		# Band 1: 237,100 → 0 + 237,100 × 18% = 42,678
		self.assertAlmostEqual(self.calculator._sars_tax_formula(237100), 42678, places=0)
		# Band 3: 512,800 → 77,362 + (512,800−370,501)×31% ≈ 121,475
		self.assertAlmostEqual(self.calculator._sars_tax_formula(512800), 121475, delta=1)
		# Old accumulation bug would give ≈ 241,514 for 512,800; must be far below that
		self.assertLess(self.calculator._sars_tax_formula(512800), 200000)

	def test_employee_over_65_gets_secondary_rebate(self):
		"""Age comes from the slip's employee date of birth (not settings)."""
		from datetime import date
		get_value = sys.modules["frappe"].db.get_value
		self.settings.rebate_secondary = 9444
		self.settings.threshold_65_74 = 148217
		slip = make_salary_slip(30000)
		slip.end_date = None
		try:
			young = get_amount(self.calculator.compute(slip), "PAYE")
			get_value.return_value = date(date.today().year - 70, 1, 1)
			senior = get_amount(self.calculator.compute(slip), "PAYE")
		finally:
			get_value.return_value = None
		self.assertAlmostEqual(young - senior, 9444 / 12, places=1)


if __name__ == "__main__":
	unittest.main()
