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
            nssa_annual_ceiling=1914360, nssa_rate=4.5,
            aids_levy_rate=3, tax_free_threshold=100,
            currency_mode="USD",
        ))

    def test_nssa_capped(self):
        r = self.calc.compute(slip(200000))
        # Ceiling: 1,914,360/12 = 159,530; 4.5% = 7,178.85
        self.assertAlmostEqual(r["NSSA Pension Employee"]["amount"], 7178.85, delta=1)

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
        # Ceiling: 8 x 75,000 = 600,000
        # INSS emp: 3.5% of 600k = 21,000
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 21000, delta=1)


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


class TestBurkinaFaso(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.burkina_faso import BurkinaFasoCalculator
        self.calc = BurkinaFasoCalculator(MockSettings(
            minimum_wage=65000, cnss_employee_rate=5.5,
            cnss_employer_rate=9.5, amo_employee_rate=3,
            amo_employer_rate=5, pit_threshold=500000,
        ))

    def test_cnss_amo_pit(self):
        r = self.calc.compute(slip(1000000))
        self.assertGreater(r["CNSS Pension Employee"]["amount"], 0)
        self.assertGreater(r["AMO Health Employee"]["amount"], 0)


class TestBenin(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.benin import BeninCalculator
        self.calc = BeninCalculator(MockSettings(
            minimum_wage=65000, cnss_employee_rate=3.6,
            cnss_employer_rate=6.4, amo_employee_rate=2,
            amo_employer_rate=4, pit_threshold=500000,
        ))

    def test_cnss_amo(self):
        r = self.calc.compute(slip(800000))
        # Ceiling: 8 x 65,000 = 520,000
        # CNSS emp: 3.6% of 520k = 18,720
        self.assertAlmostEqual(r["CNSS Pension Employee"]["amount"], 18720, delta=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
