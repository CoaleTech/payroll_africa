"""Unit tests for Tier 3 country calculators (9 countries)."""

import unittest
from unittest.mock import MagicMock
import sys
sys.path.insert(0, '/mnt/agents/output')

frappe_mock = MagicMock()
frappe_mock.utils = MagicMock()
frappe_mock.utils.flt = lambda v, p=None: float(v) if v is not None else 0.0
sys.modules['frappe'] = frappe_mock
sys.modules['frappe.utils'] = frappe_mock.utils

from payroll_africa.calculators.base import BaseCalculator


class MockSettings:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        for band_name in ['paye_bands', 'pit_bands', 'income_tax_bands']:
            if not hasattr(self, band_name):
                setattr(self, band_name, [])
    def get(self, key, default=None):
        return getattr(self, key, default)


def slip(gross, basic=None):
    s = MagicMock()
    s.gross_pay = gross
    earnings = []
    if basic is not None:
        e = MagicMock()
        e.salary_component = "Basic Salary"
        e.amount = basic
        earnings.append(e)
    s.earnings = earnings
    return s


class TestGabon(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.gabon import GabonCalculator
        self.calc = GabonCalculator(MockSettings(
            use_2026_reform=1, cnss_total_rate=23, cnss_employee_rate=5,
            cnss_employer_rate=18, cnss_ceiling=1500000,
            pit_threshold_annual=2160000,
        ))

    def test_2026_reform_rates(self):
        r = self.calc.compute(slip(2000000))
        # 5% of 1,500,000 = 75,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 75000, delta=1)
        # 18% of 1,500,000 = 270,000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 270000, delta=1)

    def test_pit(self):
        r = self.calc.compute(slip(3000000))
        self.assertIn("PIT", r)
        # Annual: 36M; after CNSS: 35.1M
        # Tax: 0.84M*5% + 1.8M*10% + 2.4M*15% + 2.4M*20% + 2.4M*25% + 12M*30% + 11.1M*35%
        self.assertGreater(r["PIT"]["amount"], 0)

    def test_below_threshold(self):
        r = self.calc.compute(slip(100000))
        self.assertNotIn("PIT", r)


class TestCongo(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.congo import CongoCalculator
        self.calc = CongoCalculator(MockSettings(
            cnss_rate=16, cnamgs_rate=4.1, cnss_ceiling=1500000,
            cnss_employee_rate=4,
        ))

    def test_employer_contributions(self):
        r = self.calc.compute(slip(2000000))
        # CNSS: 16% of 1.5M = 240,000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 240000, delta=1)
        # CNAMGS: 4.1% of 1.5M = 61,500
        self.assertAlmostEqual(r["CNAMGS Health Employer"]["amount"], 61500, delta=1)
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])


class TestGuinea(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.guinea import GuineaCalculator
        self.calc = GuineaCalculator(MockSettings(
            minimum_wage=80000, inss_pension_employee_rate=2.5,
            inss_pension_employer_rate=5, inss_family_rate=3,
            work_injury_risk_class=1, amo_employee_rate=1.5,
            amo_employer_rate=1.5,
        ))

    def test_inss_components(self):
        r = self.calc.compute(slip(1000000))
        # Ceiling: 8 x 80,000 = 640,000
        # Pension emp: 2.5% of 640k = 16,000
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 16000, delta=1)
        self.assertTrue(r["Work Injury Insurance"]["is_employer_only"])


class TestTogo(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.togo import TogoCalculator
        self.calc = TogoCalculator(MockSettings(
            minimum_wage=65000, cnss_employee_rate=4,
            cnss_employer_rate=17.5, pit_threshold=900000,
        ))

    def test_cnss_total(self):
        r = self.calc.compute(slip(800000))
        # Ceiling: 8 x 65,000 = 520,000
        # Employee: 4% of 520k = 20,800
        # Employer: 17.5% of 520k = 91,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 20800, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 91000, delta=1)


class TestSeychelles(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.seychelles import SeychellesCalculator
        self.calc = SeychellesCalculator(MockSettings(
            social_security_rate=5, social_security_ceiling=15000,
        ))

    def test_paye_bands(self):
        r = self.calc.compute(slip(10000))
        # 8,555.50 @ 0% + 1,444.50 @ 15% = 216.68
        self.assertAlmostEqual(r["PAYE"]["amount"], 216.68, delta=1)

    def test_exempt(self):
        r = self.calc.compute(slip(8000))
        self.assertNotIn("PAYE", r)

    def test_ss_employer_only(self):
        r = self.calc.compute(slip(10000))
        self.assertTrue(r["Social Security Employer"]["is_employer_only"])


class TestSierraLeone(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.sierra_leone import SierraLeoneCalculator
        self.calc = SierraLeoneCalculator(MockSettings(
            nassit_employee_rate=5, nassit_employer_rate=10,
            nassit_ceiling=3000000,
        ))

    def test_nassit(self):
        r = self.calc.compute(slip(5000000))
        # Capped at 3M; employee 5% = 150,000
        self.assertAlmostEqual(r["NASSIT Employee"]["amount"], 150000, delta=1)
        self.assertAlmostEqual(r["NASSIT Employer"]["amount"], 300000, delta=1)


class TestChad(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.chad import ChadCalculator
        self.calc = ChadCalculator(MockSettings(
            minimum_wage=75000, cnps_pension_employee_rate=3.5,
            cnps_pension_employer_rate=7, cnps_family_rate=7.5,
            work_injury_risk_class=1,
        ))

    def test_cnps(self):
        r = self.calc.compute(slip(1000000))
        # Ceiling: 8 x 75,000 = 600,000
        # Pension emp: 3.5% of 600k = 21,000
        self.assertAlmostEqual(r["CNPS Pension Employee"]["amount"], 21000, delta=1)


class TestLiberia(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.liberia import LiberiaCalculator
        self.calc = LiberiaCalculator(MockSettings(
            nasscorp_employee_rate=3, nasscorp_employer_rate=4.75,
            nasscorp_ceiling=500000,
        ))

    def test_nasscorp(self):
        r = self.calc.compute(slip(800000))
        # Capped at 500k; employee 3% = 15,000
        self.assertAlmostEqual(r["NASSCorp Employee"]["amount"], 15000, delta=1)


class TestEswatini(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.eswatini import EswatiniCalculator
        self.calc = EswatiniCalculator(MockSettings(
            enpf_rate=5, enpf_cap_total=400, sdl_rate=1,
            tax_rebate_annual=8200,
        ))

    def test_enpf_capped(self):
        r = self.calc.compute(slip(10000))
        # 5% of 10,000 = 500, but cap is E200 per side
        self.assertAlmostEqual(r["ENPF Employee"]["amount"], 200, delta=1)
        self.assertAlmostEqual(r["ENPF Employer"]["amount"], 200, delta=1)

    def test_paye_with_rebate(self):
        r = self.calc.compute(slip(15000))
        # Annual: 180,000; Tax before rebate: 47,500 + (180k-200k)*0.33 = wait, 180k < 200k
        # Actually: 180k falls in 150k-200k bracket: 32,500 + (180k-150k)*0.30 = 32,500 + 9,000 = 41,500
        # After rebate: 41,500 - 8,200 = 33,300 annual = 2,775 monthly
        self.assertIn("PAYE", r)
        self.assertAlmostEqual(r["PAYE"]["amount"], 2715, delta=100)

    def test_sdl_employer_only(self):
        r = self.calc.compute(slip(10000))
        self.assertTrue(r["Skills Development Levy"]["is_employer_only"])
        self.assertAlmostEqual(r["Skills Development Levy"]["amount"], 100, delta=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
