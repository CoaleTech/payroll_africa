"""Unit tests for Tier 2 country calculators (8 countries)."""

import unittest
from unittest.mock import MagicMock

import sys
sys.modules["frappe"] = MagicMock()
sys.modules["frappe.utils"] = MagicMock()
sys.modules["frappe.utils"].flt = lambda v, p=None: float(v) if v is not None else 0.0

from payroll_africa.calculators.base import BaseCalculator


class MockSettings:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        for band_name in ['paye_bands', 'pit_bands', 'pit_bands', 'income_tax_bands',
                          'amo_bands', 'crtv_bands', 'taxe_communale_bands']:
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


class TestCameroon(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.cameroon import CameroonCalculator
        self.calc = CameroonCalculator(MockSettings(
            cnps_ceiling=750000, cnps_pension_employee_rate=4.2,
            cnps_pension_employer_rate=4.2, family_allowances_rate=7,
            work_injury_risk_class=1, cfc_employee_rate=1,
            cfc_employer_rate=1.5, fne_rate=1,
            professional_abatement_rate=30, standard_deduction=500000,
            pit_exemption_monthly=62000, cac_surcharge_rate=10,
            taxe_communale_max=2520, crtv_bands=[], taxe_communale_bands=[],
        ))

    def test_cnps_capped(self):
        r = self.calc.compute(slip(1000000))
        # CNPS emp: 4.2% of 750,000 = 31,500
        self.assertAlmostEqual(r["CNPS Pension Employee"]["amount"], 31500, delta=1)
        self.assertTrue(r["CNPS Pension Employer"]["is_employer_only"])

    def test_pit_calculation(self):
        r = self.calc.compute(slip(500000))
        # Annual: 6,000,000; less CNPS 252,000; less 30% abatement 1,800,000; less 500,000 = 3,448,000
        # Tax: 2M@11% + 1M@16.5% + 448k@27.5% = 220k + 165k + 123.2k = 508.2k annual = 42.35k monthly
        self.assertIn("PIT", r)
        self.assertGreater(r["PIT"]["amount"], 40000)

    def test_below_exemption(self):
        r = self.calc.compute(slip(50000))
        self.assertNotIn("PIT", r)

    def test_crtv(self):
        r = self.calc.compute(slip(2000000))
        self.assertIn("CRTV Royalty", r)


class TestZimbabwe(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.zimbabwe import ZimbabweCalculator
        self.calc = ZimbabweCalculator(MockSettings(
            nssa_annual_ceiling=8400, nssa_rate=4.5,
            aids_levy_rate=3, tax_free_threshold=100,
            currency_mode="USD",
        ))

    def test_nssa_capped(self):
        r = self.calc.compute(slip(200000))
        # Ceiling: 8,400/12 = 700/month; 4.5% = 31.50
        self.assertAlmostEqual(r["NSSA Pension Employee"]["amount"], 31.50, delta=1)

    def test_paye_formula(self):
        r = self.calc.compute(slip(2000))
        # After NSSA: ~2000 - 90 = 1910
        # PAYE: 1910 x 30% - 85 = 488
        self.assertIn("PAYE", r)
        self.assertGreater(r["PAYE"]["amount"], 0)

    def test_aids_levy(self):
        r = self.calc.compute(slip(2000))
        paye = r["PAYE"]["amount"]
        aids = r["AIDS Levy"]["amount"]
        self.assertAlmostEqual(aids, paye * 0.03, places=2)

    def test_below_threshold(self):
        r = self.calc.compute(slip(50))
        self.assertNotIn("PAYE", r)


class TestMauritius(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.mauritius import MauritiusCalculator
        self.calc = MauritiusCalculator(MockSettings(
            nsf_ceiling=25475, nsf_employee_rate=1, nsf_employer_rate=2.5,
            csg_rate=1.5, hrdc_rate=1.5, prgf_applicable=1, prgf_rate=2.5,
            prgf_exemption_threshold=200000, exempt_threshold_monthly=38462,
            fair_share_applicable=1, fair_share_threshold=12000000,
            fair_share_rate=15,
        ))

    def test_nsf_capped(self):
        r = self.calc.compute(slip(50000))
        # Employee: 1% of 25,475 = 254.75
        self.assertAlmostEqual(r["NSF Employee"]["amount"], 254.75, places=2)
        # Employer: 2.5% of 25,475 = 636.88
        self.assertAlmostEqual(r["NSF Employer"]["amount"], 636.88, places=2)

    def test_paye_simplified(self):
        r = self.calc.compute(slip(100000))
        # Annual: 1,200,000
        # Tax: 500k@0% + 500k@10% + 200k@20% = 0 + 50k + 40k = 90k annual = 7.5k monthly
        self.assertAlmostEqual(r["PAYE"]["amount"], 7500, delta=100)

    def test_exempt(self):
        r = self.calc.compute(slip(30000))
        self.assertNotIn("PAYE", r)

    def test_hrdc_employer_only(self):
        r = self.calc.compute(slip(50000))
        self.assertTrue(r["HRDC Levy"]["is_employer_only"])
        self.assertAlmostEqual(r["HRDC Levy"]["amount"], 750, places=2)

    def test_fair_share(self):
        r = self.calc.compute(slip(1200000))
        # Annual: 14,400,000 > 12M threshold
        # FSC: (14.4M - 12M) x 15% = 360k annual = 30k monthly
        self.assertIn("Fair Share Contribution", r)
        self.assertAlmostEqual(r["Fair Share Contribution"]["amount"], 30000, delta=500)


class TestSenegal(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.senegal import SenegalCalculator
        self.calc = SenegalCalculator(MockSettings(
            ipres_ceiling=299000, ipres_employee_rate=5.6,
            ipres_employer_rate=8.4, css_ceiling=299000,
            css_employee_rate=3, css_employer_rate=5,
            amo_applicable=1, amo_employee_rate=3, amo_employer_rate=3,
            amo_ceiling=299000, tax_free_threshold_annual=630000,
            child_deduction=100000, number_of_dependent_children=2,
            max_deductible_children=6,
        ))

    def test_ipres_capped(self):
        r = self.calc.compute(slip(500000))
        # IPRES emp: 5.6% of 299,000 = 16,744
        self.assertAlmostEqual(r["IPRES Pension Employee"]["amount"], 16744, delta=1)

    def test_amo_applied(self):
        r = self.calc.compute(slip(500000))
        self.assertIn("AMO Health Employee", r)
        self.assertIn("AMO Health Employer", r)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["IPRES Pension Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["IPRES Pension Employer"]["amount"], 0, delta=1)
        self.assertNotIn("Income Tax", r)

    def test_key_components(self):
        r = self.calc.compute(slip(200000))
        # gross 200,000 < IPRES ceiling 299,000 so base = 200,000
        # IPRES emp: 5.6% of 200,000 = 11,200
        # CSS emp: 3% of 200,000 = 6,000
        self.assertAlmostEqual(r["IPRES Pension Employee"]["amount"], 11200, delta=1)
        self.assertAlmostEqual(r["CSS Health Employee"]["amount"], 6000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(200000))
        self.assertTrue(r["IPRES Pension Employer"]["is_employer_only"])
        self.assertTrue(r["CSS Health Employer"]["is_employer_only"])
        self.assertFalse(r["IPRES Pension Employee"]["is_employer_only"])

    def test_below_pit_threshold(self):
        # Monthly gross 52,000 → annual 624,000 ≤ threshold 630,000 → no Income Tax
        r = self.calc.compute(slip(52000))
        self.assertNotIn("Income Tax", r)


class TestMali(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.mali import MaliCalculator
        self.calc = MaliCalculator(MockSettings(
            minimum_wage=75000, inss_employee_rate=3.5,
            inss_employer_rate=7.5, amo_employee_rate=2,
            amo_employer_rate=3.5, pit_threshold=650000,
        ))

    def test_inss_amo(self):
        r = self.calc.compute(slip(1000000))
        # No ceiling (INPS on total salary); INSS emp: 3.5% of 1,000,000 = 35,000
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 35000, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(500000))
        # Ceiling: 8 x 75,000 = 600,000; gross 500,000 < ceiling so base = 500,000
        # INSS emp: 3.5% of 500,000 = 17,500
        # AMO emp: 2% of 500,000 = 10,000
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 17500, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 10000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertTrue(r["INSS Pension Employer"]["is_employer_only"])
        self.assertTrue(r["AMO Health Employer"]["is_employer_only"])
        self.assertFalse(r["INSS Pension Employee"]["is_employer_only"])
        self.assertFalse(r["AMO Health Employee"]["is_employer_only"])

    def test_ceiling(self):
        r = self.calc.compute(slip(2000000))
        # No ceiling; INSS emp: 3.5% of 2,000,000 = 70,000
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 70000, delta=1)
        # At twice the gross the result doubles (no ceiling)
        r2 = self.calc.compute(slip(4000000))
        self.assertAlmostEqual(r2["INSS Pension Employee"]["amount"], 140000, delta=1)

    def test_below_pit_threshold(self):
        # Monthly gross of 50,000 → annual 600,000 ≤ threshold 650,000 → no PIT
        r = self.calc.compute(slip(50000))
        self.assertNotIn("PIT", r)


class TestNiger(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.niger import NigerCalculator
        self.calc = NigerCalculator(MockSettings(
            minimum_wage=70000, cnss_employee_rate=5.25,
            cnss_employer_rate=8.5, amo_employee_rate=2.5,
            amo_employer_rate=4.5, pit_threshold=500000,
        ))

    def test_cnss_amo(self):
        r = self.calc.compute(slip(800000))
        # Ceiling: 8 x 70,000 = 560,000
        # CNSS emp: 5.25% of 560k = 29,400
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 29400, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(400000))
        # Ceiling: 8 x 70,000 = 560,000; gross 400,000 < ceiling so base = 400,000
        # CNSS emp: 5.25% of 400,000 = 21,000
        # AMO emp: 2.5% of 400,000 = 10,000
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 21000, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 10000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertTrue(r["CNSS Pension Employer"]["is_employer_only"])
        self.assertTrue(r["AMO Health Employer"]["is_employer_only"])
        self.assertFalse(r["CNSS Pension Employee"]["is_employer_only"])
        self.assertFalse(r["AMO Health Employee"]["is_employer_only"])

    def test_ceiling(self):
        r = self.calc.compute(slip(2000000))
        # Ceiling = 8 x 70,000 = 560,000
        # CNSS emp capped: 5.25% of 560,000 = 29,400
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 29400, delta=1)

    def test_below_pit_threshold(self):
        # Monthly gross 40,000 → annual 480,000 ≤ threshold 500,000 → no PIT
        r = self.calc.compute(slip(40000))
        self.assertNotIn("PIT", r)


class TestBurkinaFaso(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.burkina_faso import BurkinaFasoCalculator
        self.calc = BurkinaFasoCalculator(MockSettings(
            minimum_wage=45000, cnss_ceiling=800000, cnss_employee_rate=8,
            cnss_employer_rate=17.5, amo_employee_rate=2.5,
            amo_employer_rate=2.5, pit_threshold=30000,
        ))

    def test_cnss_amo_pit(self):
        r = self.calc.compute(slip(1000000))
        self.assertGreater(r["CNSS Pension Employee"]["amount"], 0)
        self.assertGreater(r["AMO Health Employee"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(400000))
        # ceiling 800,000; base 400,000; CNSS emp 8%=32,000; AMO emp 2.5%=10,000
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 32000, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 10000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertTrue(r["CNSS Pension Employer"]["is_employer_only"])
        self.assertTrue(r["AMO Health Employer"]["is_employer_only"])
        self.assertFalse(r["CNSS Pension Employee"]["is_employer_only"])
        self.assertFalse(r["AMO Health Employee"]["is_employer_only"])

    def test_ceiling(self):
        r = self.calc.compute(slip(2000000))
        # Ceiling 800,000; CNSS emp 8% of 800,000 = 64,000
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 64000, delta=1)

    def test_below_pit_threshold(self):
        # Monthly IUTS threshold 30,000; gross 30,000: taxable ~26,850 < 30,000 -> no PIT
        r = self.calc.compute(slip(30000))
        self.assertNotIn("PIT", r)


class TestBenin(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.benin import BeninCalculator
        self.calc = BeninCalculator(MockSettings(
            minimum_wage=52000, cnss_ceiling=0, cnss_employee_rate=3.6,
            cnss_employer_rate=15.4, amo_employee_rate=0,
            amo_employer_rate=0, pit_threshold=60000,
        ))

    def test_cnss_amo(self):
        r = self.calc.compute(slip(800000))
        # No ceiling; CNSS emp 3.6% of 800,000 = 28,800
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 28800, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(300000))
        # No ceiling; CNSS emp 3.6% of 300,000 = 10,800; AMO 0 (no separate AMU)
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 10800, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 0, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertTrue(r["CNSS Pension Employer"]["is_employer_only"])
        self.assertTrue(r["AMO Health Employer"]["is_employer_only"])
        self.assertFalse(r["CNSS Pension Employee"]["is_employer_only"])
        self.assertFalse(r["AMO Health Employee"]["is_employer_only"])

    def test_ceiling(self):
        r = self.calc.compute(slip(2000000))
        # No ceiling; CNSS emp 3.6% of 2,000,000 = 72,000
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 72000, delta=1)

    def test_below_pit_threshold(self):
        # Monthly gross 40,000 → annual 480,000 ≤ threshold 500,000 → no PIT
        r = self.calc.compute(slip(40000))
        self.assertNotIn("PIT", r)


class TestAlgeria(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.algeria import AlgeriaCalculator
        self.calc = AlgeriaCalculator(MockSettings(
            cnas_employee_rate=9,
            cnas_employer_rate=25.5,
        ))

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNAS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNAS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(50000))
        # CNAS emp: 9% of 50,000 = 4,500
        # CNAS empr: 25.5% of 50,000 = 12,750
        self.assertAlmostEqual(r["CNAS Employee"]["amount"], 4500, delta=1)
        self.assertAlmostEqual(r["CNAS Employer"]["amount"], 12750, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(50000))
        self.assertTrue(r["CNAS Employer"]["is_employer_only"])
        self.assertFalse(r["CNAS Employee"]["is_employer_only"])

    def test_pit_above_threshold(self):
        # Monthly 25,000 -> annual 300,000 > 240,000 threshold -> PIT expected
        # taxable after CNAS: 22,750/mo -> annual 273,000
        # tax: (273,000 - 240,000) x 23% = 7,590 annual -> 632.5 monthly
        r = self.calc.compute(slip(25000))
        self.assertIn("PIT", r)
        self.assertAlmostEqual(r["PIT"]["amount"], 632.5, delta=5)

    def test_below_pit_threshold(self):
        # Monthly 19,000 → after CNAS 17,290 → annual 207,480 ≤ 240,000 → no PIT
        r = self.calc.compute(slip(19000))
        self.assertNotIn("PIT", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
