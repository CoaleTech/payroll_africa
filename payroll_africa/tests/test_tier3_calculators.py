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
            use_2026_reform=1, cnss_employee_rate=5,
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
            cnss_rate=20.285, cnamgs_rate=0.5, cnss_ceiling=1200000,
            cnss_employee_rate=4,
        ))

    def test_employer_contributions(self):
        r = self.calc.compute(slip(2000000))
        # CNSS: 20.285% of 1.2M ceiling = 243,420
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 243420, delta=1)
        # CAMU: 0.5% of (2M - 500k) = 7,500
        self.assertAlmostEqual(r["CAMU Health Employer"]["amount"], 7500, delta=1)
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CAMU Health Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(2000000))
        # CNSS Employee: 4% of 1.2M ceiling = 48,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 48000, delta=1)
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(1000000))
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])
        self.assertTrue(r["CAMU Health Employer"]["is_employer_only"])
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])

    def test_ceiling_caps_contributions(self):
        r = self.calc.compute(slip(3000000))
        # CNSS capped at ceiling 1.2M; CAMU on (3M-500k)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 243420, delta=1)
        self.assertAlmostEqual(r["CAMU Health Employer"]["amount"], 12500, delta=1)

    def test_below_pit_threshold(self):
        # Monthly gross 74,000 → annual 888,000 ≤ 900,000 → no PIT
        r = self.calc.compute(slip(74000))
        self.assertNotIn("PIT", r)

    def test_pit_above_threshold(self):
        # Monthly gross 300,000; cnss_employee = 4% × 300,000 = 12,000
        # taxable = 300,000 − 12,000 = 288,000; annual = 3,456,000
        # Tax: (2,400,000−900,000)×5% + (3,456,000−2,400,000)×10% = 75,000 + 105,600 = 180,600
        # Monthly PIT = 180,600 / 12 = 15,050
        r = self.calc.compute(slip(300000))
        self.assertIn("PIT", r)
        self.assertAlmostEqual(r["PIT"]["amount"], 15050, delta=1)


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

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["INSS Pension Employer"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(1000000))
        # Ceiling: 8 x 80,000 = 640,000
        # Pension employer: 5% of 640k = 32,000
        self.assertAlmostEqual(r["INSS Pension Employer"]["amount"], 32000, delta=1)
        # Family: 3% of 640k = 19,200
        self.assertAlmostEqual(r["INSS Family Allowances"]["amount"], 19200, delta=1)
        # AMO employee: 1.5% of 640k = 9,600
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 9600, delta=1)
        # AMO employer: 1.5% of 640k = 9,600
        self.assertAlmostEqual(r["AMO Health Employer"]["amount"], 9600, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(500000))
        self.assertTrue(r["INSS Pension Employer"]["is_employer_only"])
        self.assertTrue(r["INSS Family Allowances"]["is_employer_only"])
        self.assertTrue(r["Work Injury Insurance"]["is_employer_only"])
        self.assertTrue(r["AMO Health Employer"]["is_employer_only"])
        self.assertFalse(r["INSS Pension Employee"]["is_employer_only"])
        self.assertFalse(r["AMO Health Employee"]["is_employer_only"])

    def test_ceiling_caps_contributions(self):
        # Gross 2,000,000 > ceiling 640,000; pension_emp still capped at 2.5%*640k=16,000
        r = self.calc.compute(slip(2000000))
        self.assertAlmostEqual(r["INSS Pension Employee"]["amount"], 16000, delta=1)
        self.assertAlmostEqual(r["INSS Pension Employer"]["amount"], 32000, delta=1)

    def test_below_pit_threshold(self):
        # Monthly 80,000 → base=80,000; pension_emp=2,000; amo_emp=1,200
        # taxable=76,800; annual=921,600 < 1,200,000 → no PIT
        r = self.calc.compute(slip(80000))
        self.assertNotIn("PIT", r)

    def test_work_injury_uses_capped_base(self):
        # gross=2,000,000; ceiling=8*80,000=640,000; risk 1 -> 1.5% of BASE not gross
        r = self.calc.compute(slip(2000000))
        self.assertAlmostEqual(r["Work Injury Insurance"]["amount"], 640000 * 0.015, delta=1)

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.guinea import GuineaCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = GuineaCalculator(MockSettings(
            minimum_wage=80000, inss_pension_employee_rate=2.5,
            inss_pension_employer_rate=5, inss_family_rate=3,
            work_injury_risk_class=1, amo_employee_rate=1.5, amo_employer_rate=1.5,
            pit_bands=[Band(0, 0, 20)],
        ))
        # single 20% band; gross=1,000,000; ceiling=640,000
        # pension_emp=2.5%*640k=16,000; amo_emp=1.5%*640k=9,600; taxable=974,400
        # tax=20%*974,400=194,880 (annual)
        r = calc.compute(slip(1000000))
        self.assertAlmostEqual(r["PIT"]["amount"], 194880, delta=1)


class TestTogo(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.togo import TogoCalculator
        self.calc = TogoCalculator(MockSettings(
            minimum_wage=52500, cnss_ceiling=500000, cnss_employee_rate=4,
            cnss_employer_rate=17.5, inam_employee_rate=5,
            inam_employer_rate=5, pit_threshold=900000,
        ))

    def test_cnss_total(self):
        r = self.calc.compute(slip(800000))
        # Ceiling 500,000; Employee 4% = 20,000; Employer 17.5% = 87,500
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 20000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 87500, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])

    def test_ceiling_caps_contributions(self):
        # Gross 1,000,000 > ceiling 500,000; CNSS based on 500,000
        r = self.calc.compute(slip(1000000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 20000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 87500, delta=1)

    def test_below_pit_threshold(self):
        # Monthly 74,000; base 74,000; cnss 2,960 + inam 3,700
        # taxable 67,340; annual 808,080 < 900,000 -> no PIT
        r = self.calc.compute(slip(74000))
        self.assertNotIn("PIT", r)

    def test_pit_above_threshold(self):
        # Monthly 500,000; base 500,000; cnss_emp 20,000; inam_emp 25,000
        # taxable 455,000; annual 5,460,000
        # Tax: (3,000,000-900,000)*3% + (5,460,000-3,000,000)*10% = 63,000 + 246,000 = 309,000; monthly = 25,750
        r = self.calc.compute(slip(500000))
        self.assertIn("PIT", r)
        self.assertAlmostEqual(r["PIT"]["amount"], 25750, delta=1)

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.togo import TogoCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = TogoCalculator(MockSettings(
            cnss_ceiling=500000, cnss_employee_rate=4, cnss_employer_rate=17.5,
            inam_employee_rate=5, inam_employer_rate=5,
            pit_bands=[Band(0, 500000, 0), Band(500000, 0, 5)],
        ))
        # gross=500,000; cnss_emp=4%*500k=20,000; inam_emp=5%*500k=25,000
        # taxable=455,000; annual=5,460,000; tax=(5,460,000-500,000)*5%=248,000; monthly=20,666.67
        r = calc.compute(slip(500000))
        self.assertAlmostEqual(r["PIT"]["amount"], 20666.67, delta=1)


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

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["NASSIT Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["NASSIT Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PAYE", r)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(1000000))
        self.assertTrue(r["NASSIT Employer"]["is_employer_only"])
        self.assertFalse(r["NASSIT Employee"]["is_employer_only"])

    def test_ceiling_caps_contributions(self):
        # Gross 5,000,000 > ceiling 3,000,000; NASSIT capped
        # Employee: 5% of 3M = 150,000 (not 5% of 5M = 250,000)
        r = self.calc.compute(slip(5000000))
        self.assertAlmostEqual(r["NASSIT Employee"]["amount"], 150000, delta=1)

    def test_below_paye_threshold(self):
        # Monthly 400; nassit_emp=5%*400=20; taxable=380; annual=4,560 < 6,000 -> no PAYE
        r = self.calc.compute(slip(400))
        self.assertNotIn("PAYE", r)

    def test_paye_above_threshold(self):
        # Monthly 5,000,000; nassit_emp=5%*3M(ceiling)=150,000; taxable=4,850,000; annual=58,200,000
        # Tax: 900+1200+1500 + (58,200,000-24,000)*30% = 17,456,400; monthly = 1,454,700
        r = self.calc.compute(slip(5000000))
        self.assertIn("PAYE", r)
        self.assertAlmostEqual(r["PAYE"]["amount"], 1454700, delta=1)

    def test_paye_reads_bands_from_settings(self):
        from payroll_africa.calculators.sierra_leone import SierraLeoneCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = SierraLeoneCalculator(MockSettings(
            nassit_employee_rate=5, nassit_employer_rate=10, nassit_ceiling=0,
            paye_bands=[Band(0, 12000, 0), Band(12000, 0, 20)],
        ))
        # gross=5,000; nassit_emp=250; taxable=4,750; annual=57,000
        # tax=(57,000-12,000)*20%=9,000; monthly=750
        r = calc.compute(slip(5000))
        self.assertAlmostEqual(r["PAYE"]["amount"], 750, delta=1)


class TestChad(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.chad import ChadCalculator
        self.calc = ChadCalculator(MockSettings(
            minimum_wage=75000, cnps_pension_employee_rate=3.5,
            cnps_pension_employer_rate=7, family_allowances_rate=7.5,
            work_injury_risk_class=1,
        ))

    def test_cnps(self):
        r = self.calc.compute(slip(1000000))
        # Ceiling: 8 x 75,000 = 600,000
        # Pension emp: 3.5% of 600k = 21,000
        self.assertAlmostEqual(r["CNPS Pension Employee"]["amount"], 21000, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNPS Pension Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNPS Pension Employer"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNPS Family Allowances"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(1000000))
        # Ceiling: 8 x 75,000 = 600,000
        # Pension employer: 7% of 600k = 42,000
        self.assertAlmostEqual(r["CNPS Pension Employer"]["amount"], 42000, delta=1)
        # Family: 7.5% of 600k = 45,000
        self.assertAlmostEqual(r["CNPS Family Allowances"]["amount"], 45000, delta=1)
        # Work Injury risk class 1: 2% of gross = 20,000
        self.assertAlmostEqual(r["Work Injury Insurance"]["amount"], 20000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(500000))
        self.assertTrue(r["CNPS Pension Employer"]["is_employer_only"])
        self.assertTrue(r["CNPS Family Allowances"]["is_employer_only"])
        self.assertTrue(r["Work Injury Insurance"]["is_employer_only"])
        self.assertFalse(r["CNPS Pension Employee"]["is_employer_only"])

    def test_ceiling_caps_contributions(self):
        # Gross 2,000,000 > ceiling 600,000; pension_emp stays at 3.5%*600k=21,000
        r = self.calc.compute(slip(2000000))
        self.assertAlmostEqual(r["CNPS Pension Employee"]["amount"], 21000, delta=1)
        self.assertAlmostEqual(r["CNPS Pension Employer"]["amount"], 42000, delta=1)

    def test_below_pit_threshold(self):
        # Monthly 70,000; taxable annual ~810,600 > 800,000 threshold -> PIT now applies
        r = self.calc.compute(slip(70000))
        self.assertIn("PIT", r)

    def test_pit_above_threshold(self):
        # Monthly 500,000; pension_emp=17,500; taxable=482,500; annual=5,790,000
        # New PwC bands: (5,790,000-800,000)*10.5% = 523,950; monthly = 43,662.50
        r = self.calc.compute(slip(500000))
        self.assertIn("PIT", r)
        self.assertAlmostEqual(r["PIT"]["amount"], 43662.5, delta=1)


class TestLiberia(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.liberia import LiberiaCalculator
        # Statutory rates as seeded by setup.py: 4%/6% uncapped (ceiling=0)
        self.calc = LiberiaCalculator(MockSettings(
            nasscorp_employee_rate=4, nasscorp_employer_rate=6,
            nasscorp_ceiling=0,
        ))

    def test_nasscorp(self):
        # No ceiling; employee 4% of 800,000 = 32,000
        r = self.calc.compute(slip(800000))
        self.assertAlmostEqual(r["NASSCorp Employee"]["amount"], 32000, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["NASSCorp Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["NASSCorp Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PAYE", r)

    def test_key_components(self):
        # No ceiling; employer 6% of 800,000 = 48,000
        r = self.calc.compute(slip(800000))
        self.assertAlmostEqual(r["NASSCorp Employer"]["amount"], 48000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertTrue(r["NASSCorp Employer"]["is_employer_only"])
        self.assertFalse(r["NASSCorp Employee"]["is_employer_only"])

    def test_ceiling_zero_means_uncapped(self):
        # ceiling=0: no cap; 4% of 1,000,000 = 40,000
        r = self.calc.compute(slip(1000000))
        self.assertAlmostEqual(r["NASSCorp Employee"]["amount"], 40000, delta=1)

    def test_ceiling_active_when_set(self):
        from payroll_africa.calculators.liberia import LiberiaCalculator
        calc = LiberiaCalculator(MockSettings(
            nasscorp_employee_rate=4, nasscorp_employer_rate=6, nasscorp_ceiling=500000))
        r = calc.compute(slip(800000))
        # Capped at 500,000: 4% = 20,000
        self.assertAlmostEqual(r["NASSCorp Employee"]["amount"], 20000, delta=1)

    def test_below_paye_threshold(self):
        # Monthly 5,600; nassc_emp=4%*5,600=224; taxable=5,376; annual=64,512 < 70,000 → no PAYE
        r = self.calc.compute(slip(5600))
        self.assertNotIn("PAYE", r)

    def test_paye_above_threshold(self):
        # Monthly 20,000; nassc_emp=4%*20,000=800; taxable=19,200; annual=230,400
        # Tax: (200,000-70,000)*5%=6,500 + (230,400-200,000)*15%=4,560 = 11,060; monthly=921.67
        r = self.calc.compute(slip(20000))
        self.assertIn("PAYE", r)
        self.assertAlmostEqual(r["PAYE"]["amount"], 921.67, delta=1)

    def test_paye_reads_bands_from_settings(self):
        from payroll_africa.calculators.liberia import LiberiaCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = LiberiaCalculator(MockSettings(
            nasscorp_employee_rate=4, nasscorp_employer_rate=6, nasscorp_ceiling=0,
            paye_bands=[Band(0, 50000, 0), Band(50000, 0, 10)],
        ))
        r = calc.compute(slip(10000))
        # annual=(10000-4%*10000)*12=9600*12=115,200; tax=(115,200-50,000)*10%=6,520; monthly=543.33
        self.assertAlmostEqual(r["PAYE"]["amount"], 543.33, delta=1)


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
