"""Unit tests for Tier 4 country calculators (16 countries)."""

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
        # Initialise band lists so getattr returns [] (falsy) not None when not provided
        for band_name in ('paye_bands', 'pit_bands'):
            if not hasattr(self, band_name):
                setattr(self, band_name, [])
    def get(self, key, default=None):
        return getattr(self, key, default)


def slip(gross):
    s = MagicMock()
    s.gross_pay = gross
    s.earnings = []
    return s


class TestAlgeria(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.algeria import AlgeriaCalculator
        self.calc = AlgeriaCalculator(MockSettings(cnas_employee_rate=9, cnas_employer_rate=26))

    def test_cnas_pit(self):
        r = self.calc.compute(slip(300000))
        self.assertAlmostEqual(r["CNAS Employee"]["amount"], 27000, delta=1)
        # After CNAS: annual = 3.276M; tax: 240k*0 + 240k*0.20 + 480k*0.30 + 2.316M*0.35
        self.assertIn("PIT", r)

    def test_below_threshold(self):
        r = self.calc.compute(slip(20000))
        self.assertNotIn("PIT", r)


class TestLibya(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.libya import LibyaCalculator
        self.calc = LibyaCalculator(MockSettings(ssf_employee_rate=5.125, ssf_employer_rate=14.35, solidarity_fund_rate=1))

    def test_ssf_solidarity_jehad(self):
        r = self.calc.compute(slip(2000))
        self.assertAlmostEqual(r["SSF Employee"]["amount"], 102.5, delta=1)
        self.assertAlmostEqual(r["Solidarity Fund"]["amount"], 20, delta=1)
        self.assertAlmostEqual(r["Jehad Tax"]["amount"], 60, delta=1)  # 3% of 2000

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["SSF Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["SSF Employer"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["Solidarity Fund"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)
        self.assertNotIn("Jehad Tax", r)

    def test_key_components(self):
        # gross=2000: ssf_emp=5.125%*2000=102.5, ssf_empr=14.35%*2000=287
        # solidarity=1%*2000=20, jehad=3%*2000=60
        r = self.calc.compute(slip(2000))
        self.assertAlmostEqual(r["SSF Employee"]["amount"], 102.5, delta=1)
        self.assertAlmostEqual(r["SSF Employer"]["amount"], 287, delta=1)
        self.assertAlmostEqual(r["Solidarity Fund"]["amount"], 20, delta=1)
        self.assertAlmostEqual(r["Jehad Tax"]["amount"], 60, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(2000))
        self.assertTrue(r["SSF Employer"]["is_employer_only"])
        self.assertFalse(r["SSF Employee"]["is_employer_only"])
        self.assertFalse(r["Solidarity Fund"]["is_employer_only"])

    def test_jehad_rate_bands(self):
        # gross < 50: 1% => 40 * 0.01 = 0.40
        r_low = self.calc.compute(slip(40))
        self.assertAlmostEqual(r_low["Jehad Tax"]["amount"], 0.40, delta=0.01)
        # gross 50-100: 2% => 75 * 0.02 = 1.50
        r_mid = self.calc.compute(slip(75))
        self.assertAlmostEqual(r_mid["Jehad Tax"]["amount"], 1.50, delta=0.01)
        # gross > 100: 3% => 200 * 0.03 = 6.0
        r_high = self.calc.compute(slip(200))
        self.assertAlmostEqual(r_high["Jehad Tax"]["amount"], 6.0, delta=0.01)


class TestSomalia(unittest.TestCase):
    def test_no_deductions(self):
        from payroll_africa.calculators.somalia import SomaliaCalculator
        r = SomaliaCalculator(MockSettings()).compute(slip(500000))
        self.assertEqual(r, {})


class TestSouthSudan(unittest.TestCase):
    def test_no_deductions(self):
        from payroll_africa.calculators.south_sudan import SouthSudanCalculator
        r = SouthSudanCalculator(MockSettings()).compute(slip(100000))
        self.assertEqual(r, {})


class TestEquatorialGuinea(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.equatorial_guinea import EquatorialGuineaCalculator
        self.calc = EquatorialGuineaCalculator(MockSettings(minimum_wage=150000, cnss_employee_rate=4.5, cnss_employer_rate=21.5, wpf_employee_rate=0.5, wpf_employer_rate=1))

    def test_cnss(self):
        r = self.calc.compute(slip(2000000))
        # Ceiling: 8 * 150k = 1.2M
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 54000, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # ceiling = 150000 * 8 = 1,200,000; gross 500000 below ceiling
        # CNSS emp: 500000 * 4.5% = 22,500; empr: 500000 * 21.5% = 107,500
        r = self.calc.compute(slip(500000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 22500, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 107500, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(500000))
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])

    def test_below_pit_threshold(self):
        # annual PIT threshold 1,000,000; gross 70000: taxable ~66850, annual ~802200 < 1,000,000
        r = self.calc.compute(slip(70000))
        self.assertNotIn("PIT", r)


class TestMauritania(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.mauritania import MauritaniaCalculator
        self.calc = MauritaniaCalculator(MockSettings(cnss_ceiling=15000, cnss_employee_rate=1, cnss_employer_rate=15, cnam_employee_rate=4, cnam_employer_rate=5))

    def test_cnss_cnam(self):
        r = self.calc.compute(slip(30000))
        # CNSS capped at 15k: emp 1% = 150, empr 15% = 2,250
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 150, delta=1)
        # CNAM uncapped: emp 4% of 30k = 1,200
        self.assertAlmostEqual(r["CNAM Health Employee"]["amount"], 1200, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNAM Health Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNAM Health Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # gross=30000: cnss_base=min(30000,15000)=15000
        # cnss_emp=1%*15000=150, cnss_empr=15%*15000=2250
        # cnam_emp=4%*30000=1200, cnam_empr=5%*30000=1500
        r = self.calc.compute(slip(30000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 150, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 2250, delta=1)
        self.assertAlmostEqual(r["CNAM Health Employee"]["amount"], 1200, delta=1)
        self.assertAlmostEqual(r["CNAM Health Employer"]["amount"], 1500, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(30000))
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])
        self.assertFalse(r["CNAM Health Employee"]["is_employer_only"])
        self.assertTrue(r["CNAM Health Employer"]["is_employer_only"])

    def test_ceiling_cnss(self):
        # gross=50000 > ceiling 15000; cnss_emp still capped: 1%*15000=150
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 150, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 2250, delta=1)
        # CNAM uncapped: 4%*50000=2000
        self.assertAlmostEqual(r["CNAM Health Employee"]["amount"], 2000, delta=1)

    def test_below_pit_threshold(self):
        # annual PIT threshold 120,000; gross=5000:
        # cnss_emp=50, cnam_emp=200, taxable=4750, annual=57000 < 120000 => no PIT
        r = self.calc.compute(slip(5000))
        self.assertNotIn("PIT", r)

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.mauritania import MauritaniaCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = MauritaniaCalculator(MockSettings(
            cnss_ceiling=15000, cnss_employee_rate=1, cnss_employer_rate=15,
            cnam_employee_rate=4, cnam_employer_rate=5,
            pit_bands=[Band(0, 50000, 0), Band(50000, 0, 20)],
        ))
        # gross=30,000; cnss_emp=1%*15,000=150; cnam_emp=4%*30,000=1,200
        # taxable=28,650; annual=343,800; tax=(343,800-50,000)*20%=58,760; monthly=4,896.67
        r = calc.compute(slip(30000))
        self.assertAlmostEqual(r["PIT"]["amount"], 4896.67, delta=1)


class TestCAR(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.central_african_republic import CentralAfricanRepublicCalculator
        self.calc = CentralAfricanRepublicCalculator(MockSettings(minimum_wage=50000, cnss_employee_rate=3, cnss_employer_rate=15))

    def test_cnss(self):
        r = self.calc.compute(slip(500000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # ceiling = 50000 * 8 = 400000; gross 200000 below ceiling
        # CNSS emp: 200000 * 3% = 6,000; empr: 200000 * 15% = 30,000
        r = self.calc.compute(slip(200000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 6000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 30000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(200000))
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross 600000 > ceiling 400000; CNSS emp = 400000 * 3% = 12,000
        r = self.calc.compute(slip(600000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 12000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 60000, delta=1)

    def test_below_pit_threshold(self):
        # annual PIT threshold 600,000; gross 40000: taxable ~38800, annual ~465600 < 600000
        r = self.calc.compute(slip(40000))
        self.assertNotIn("PIT", r)


class TestDjibouti(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.djibouti import DjiboutiCalculator
        self.calc = DjiboutiCalculator(MockSettings(minimum_wage=40000, cnss_ceiling=400000, cnss_employee_rate=2, cnss_employer_rate=5))

    def test_cnss(self):
        r = self.calc.compute(slip(400000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # ceiling 400000; gross 200000 below ceiling; CNSS emp 2%=4000, empr 5%=10000
        r = self.calc.compute(slip(200000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 4000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 10000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(200000))
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross 500000 > ceiling 400000; CNSS emp = 400000 * 2% = 8,000
        r = self.calc.compute(slip(500000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 8000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 20000, delta=1)

    def test_below_pit_threshold(self):
        # annual PIT threshold 240,000; gross 20000: taxable ~19600, annual ~235200 < 240000
        r = self.calc.compute(slip(20000))
        self.assertNotIn("PIT", r)


class TestGuineaBissau(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.guinea_bissau import GuineaBissauCalculator
        self.calc = GuineaBissauCalculator(MockSettings(minimum_wage=45000, inss_employee_rate=8, inss_employer_rate=14))

    def test_inss_pit(self):
        r = self.calc.compute(slip(1000000))
        # Ceiling: 8 * 45k = 360k; INSS emp: 8% of 360k = 28,800
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 28800, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # ceiling = 45000 * 8 = 360000; gross 100000 below ceiling
        # INSS emp: 100000 * 8% = 8,000; empr: 100000 * 14% = 14,000
        r = self.calc.compute(slip(100000))
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 8000, delta=1)
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 14000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(100000))
        self.assertFalse(r["INSS Employee"]["is_employer_only"])
        self.assertTrue(r["INSS Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross 500000 > ceiling 360000; INSS emp = 360000 * 8% = 28,800
        r = self.calc.compute(slip(500000))
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 28800, delta=1)
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 50400, delta=1)

    def test_pit_present_above_zero(self):
        # PIT bracket starts at 0 (1% rate); any positive taxable income yields PIT
        r = self.calc.compute(slip(50000))
        self.assertIn("PIT", r)
        self.assertGreater(r["PIT"]["amount"], 0)

    def test_inss_ceiling_overrides_min_wage_times_8(self):
        from payroll_africa.calculators.guinea_bissau import GuineaBissauCalculator
        # inss_ceiling=200,000 overrides min_wage*8=360,000
        calc = GuineaBissauCalculator(MockSettings(
            minimum_wage=45000, inss_employee_rate=8, inss_employer_rate=14, inss_ceiling=200000,
        ))
        r = calc.compute(slip(500000))
        # Capped at 200,000: 8% = 16,000
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 16000, delta=1)

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.guinea_bissau import GuineaBissauCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = GuineaBissauCalculator(MockSettings(
            minimum_wage=45000, inss_employee_rate=8, inss_employer_rate=14,
            pit_bands=[Band(0, 0, 5)],
        ))
        # single 5% band; gross=100,000; inss_emp=8%*(8*45000=360k, cap > gross)=8,000
        # taxable=92,000; annual=1,104,000; tax=5%*1,104,000=55,200; monthly=4,600
        r = calc.compute(slip(100000))
        self.assertAlmostEqual(r["PIT"]["amount"], 4600, delta=1)


class TestLesotho(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.lesotho import LesothoCalculator
        self.calc = LesothoCalculator(MockSettings(tax_credit_annual=11640))

    def test_paye_with_credit(self):
        r = self.calc.compute(slip(10000))
        # Annual: 120k; tax before credit: 14808 + (120k-74040)*0.30 = 28,596
        # After credit: 28,596 - 11,640 = 16,956 annual = 1,413 monthly
        self.assertIn("PAYE", r)
        self.assertGreater(r["PAYE"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertNotIn("PAYE", r)

    def test_key_components(self):
        # gross=10000, annual=120000 > 74040
        # tax=14808+(120000-74040)*0.30=14808+13788=28596
        # net of credit: 28596-11640=16956; monthly=1413
        r = self.calc.compute(slip(10000))
        self.assertAlmostEqual(r["PAYE"]["amount"], 1413, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(10000))
        self.assertFalse(r["PAYE"]["is_employer_only"])

    def test_below_threshold(self):
        # gross=4000: annual=48000; tax=48000*0.20=9600; net of credit: 9600-11640<0 => no PAYE
        r = self.calc.compute(slip(4000))
        self.assertNotIn("PAYE", r)


class TestGambia(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.gambia import GambiaCalculator
        self.calc = GambiaCalculator(MockSettings(sshfc_ceiling=25000, sshfc_employee_rate=5, sshfc_employer_rate=10))

    def test_sshfc(self):
        r = self.calc.compute(slip(50000))
        # Capped at 25k; emp 5% = 1,250
        self.assertAlmostEqual(r["SSHFC Employee"]["amount"], 1250, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["SSHFC Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["SSHFC Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # gross 20000 below ceiling 25000: emp 5% = 1,000; empr 10% = 2,000
        r = self.calc.compute(slip(20000))
        self.assertAlmostEqual(r["SSHFC Employee"]["amount"], 1000, delta=1)
        self.assertAlmostEqual(r["SSHFC Employer"]["amount"], 2000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(20000))
        self.assertFalse(r["SSHFC Employee"]["is_employer_only"])
        self.assertTrue(r["SSHFC Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross 50000 > ceiling 25000; SSHFC emp = 25000 * 5% = 1,250
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["SSHFC Employee"]["amount"], 1250, delta=1)
        self.assertAlmostEqual(r["SSHFC Employer"]["amount"], 2500, delta=1)

    def test_below_pit_threshold(self):
        # annual PIT threshold 7,500; gross 600: taxable ~570, annual ~6,840 < 7,500
        r = self.calc.compute(slip(600))
        self.assertNotIn("PIT", r)

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.gambia import GambiaCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = GambiaCalculator(MockSettings(
            sshfc_ceiling=25000, sshfc_employee_rate=5, sshfc_employer_rate=10,
            pit_bands=[Band(0, 10000, 0), Band(10000, 0, 15)],
        ))
        # gross=5,000; sshfc_emp=250; taxable=4,750; annual=57,000
        # tax=(57,000-10,000)*15%=7,050; monthly=587.50
        r = calc.compute(slip(5000))
        self.assertAlmostEqual(r["PIT"]["amount"], 587.50, delta=1)


class TestEritrea(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.eritrea import EritreaCalculator
        self.calc = EritreaCalculator(MockSettings(nice_employee_rate=6, nice_employer_rate=12))

    def test_nice(self):
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["NICE Employee"]["amount"], 3000, delta=1)
        self.assertAlmostEqual(r["NICE Employer"]["amount"], 6000, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["NICE Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["NICE Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # No ceiling for NICE; gross 50000: emp 6% = 3000, empr 12% = 6000
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["NICE Employee"]["amount"], 3000, delta=1)
        self.assertAlmostEqual(r["NICE Employer"]["amount"], 6000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(50000))
        self.assertFalse(r["NICE Employee"]["is_employer_only"])
        self.assertTrue(r["NICE Employer"]["is_employer_only"])

    def test_below_pit_threshold(self):
        # annual PIT threshold 12,000; gross 800: taxable ~752, annual ~9024 < 12000
        r = self.calc.compute(slip(800))
        self.assertNotIn("PIT", r)


class TestComoros(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.comoros import ComorosCalculator
        self.calc = ComorosCalculator(MockSettings(minimum_wage=55000, cnss_employee_rate=3.5, cnss_employer_rate=10.5))

    def test_cnss(self):
        r = self.calc.compute(slip(700000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # ceiling = 55000 * 8 = 440000; gross 300000 below ceiling
        # CNSS emp: 300000 * 3.5% = 10,500; empr: 300000 * 10.5% = 31,500
        r = self.calc.compute(slip(300000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 10500, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 31500, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross 800000 > ceiling 440000; CNSS emp = 440000 * 3.5% = 15,400; empr = 440000 * 10.5% = 46,200
        r = self.calc.compute(slip(800000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 15400, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 46200, delta=1)

    def test_below_pit_threshold(self):
        # annual PIT threshold 360,000; gross 25000: taxable ~24125, annual ~289500 < 360000
        r = self.calc.compute(slip(25000))
        self.assertNotIn("PIT", r)


class TestSaoTomePrincipe(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.sao_tome_principe import SaoTomePrincipeCalculator
        self.calc = SaoTomePrincipeCalculator(MockSettings(inss_ceiling=500000, inss_employee_rate=3, inss_employer_rate=8))

    def test_inss(self):
        r = self.calc.compute(slip(400000))
        self.assertGreater(r["INSS Employee"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # gross=400000 <= ceiling 500000; inss_emp=3%*400000=12000, inss_empr=8%*400000=32000
        r = self.calc.compute(slip(400000))
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 12000, delta=1)
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 32000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(400000))
        self.assertFalse(r["INSS Employee"]["is_employer_only"])
        self.assertTrue(r["INSS Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross=700000 > ceiling 500000; inss_emp capped: 3%*500000=15000, inss_empr: 8%*500000=40000
        r = self.calc.compute(slip(700000))
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 15000, delta=1)
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 40000, delta=1)

    def test_below_pit_threshold(self):
        # PIT threshold annual=600000; gross=40000:
        # inss_emp=3%*40000=1200, taxable=38800, annual=465600 < 600000 => no PIT
        r = self.calc.compute(slip(40000))
        self.assertNotIn("PIT", r)


class TestCaboVerde(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.cabo_verde import CaboVerdeCalculator
        self.calc = CaboVerdeCalculator(MockSettings(inps_ceiling=80000, inps_employee_rate=8.5, inps_employer_rate=16, work_injury_rate=1))

    def test_inps_injury(self):
        r = self.calc.compute(slip(100000))
        # INPS capped at 80k: emp 8.5% = 6,800
        self.assertAlmostEqual(r["INPS Employee"]["amount"], 6800, delta=1)
        # Injury: 2% of capped base 80,000 = 1,600 (work injury now uses contribution base)
        self.assertAlmostEqual(r["Work Injury Insurance"]["amount"], 1600, delta=1)
        self.assertTrue(r["Work Injury Insurance"]["is_employer_only"])

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["INPS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["INPS Employer"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["Work Injury Insurance"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        r = self.calc.compute(slip(100000))
        # INPS capped at 80k: emp 8.5% = 6,800; empr 16% = 12,800
        self.assertAlmostEqual(r["INPS Employee"]["amount"], 6800, delta=1)
        self.assertAlmostEqual(r["INPS Employer"]["amount"], 12800, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(100000))
        self.assertFalse(r["INPS Employee"]["is_employer_only"])
        self.assertTrue(r["INPS Employer"]["is_employer_only"])
        self.assertTrue(r["Work Injury Insurance"]["is_employer_only"])

    def test_ceiling(self):
        # gross > ceiling: INPS emp should be capped at 80k * 8.5% = 6,800
        r = self.calc.compute(slip(200000))
        self.assertAlmostEqual(r["INPS Employee"]["amount"], 6800, delta=1)
        self.assertAlmostEqual(r["INPS Employer"]["amount"], 12800, delta=1)

    def test_below_pit_threshold(self):
        # annual PIT threshold 220,000; gross 20000: taxable ~18,300, annual ~219,600 < 220,000
        r = self.calc.compute(slip(20000))
        self.assertNotIn("PIT", r)

    def test_risk_class_2(self):
        from payroll_africa.calculators.cabo_verde import CaboVerdeCalculator
        calc = CaboVerdeCalculator(MockSettings(
            inps_ceiling=80000, inps_employee_rate=8.5, inps_employer_rate=16, work_injury_rate=2))
        r = calc.compute(slip(100000))
        # Risk class 2 = 4%; base=min(100000,80000)=80,000; injury=4%*80,000=3,200
        self.assertAlmostEqual(r["Work Injury Insurance"]["amount"], 3200, delta=1)

    def test_work_injury_uses_capped_base(self):
        # gross=200,000 > ceiling=80,000; work injury on base not gross
        r = self.calc.compute(slip(200000))
        self.assertAlmostEqual(r["Work Injury Insurance"]["amount"], 80000 * 0.02, delta=1)

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.cabo_verde import CaboVerdeCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = CaboVerdeCalculator(MockSettings(
            inps_ceiling=80000, inps_employee_rate=8.5, inps_employer_rate=16, work_injury_rate=1,
            pit_bands=[Band(0, 100000, 0), Band(100000, 0, 10)],
        ))
        # gross=50000; inps_emp=8.5%*50000=4250; taxable=45750; annual=549,000
        # tax=(549,000-100,000)*10%=44,900; monthly=3741.67
        r = calc.compute(slip(50000))
        self.assertAlmostEqual(r["PIT"]["amount"], 3741.67, delta=1)


class TestSudan(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.sudan import SudanCalculator
        self.calc = SudanCalculator(MockSettings(nsif_ceiling=100000, nsif_employee_rate=8, nsif_employer_rate=17))

    def test_nsif(self):
        r = self.calc.compute(slip(150000))
        # Capped at 100k: emp 8% = 8,000
        self.assertAlmostEqual(r["NSIF Employee"]["amount"], 8000, delta=1)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["NSIF Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["NSIF Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # gross=50000 <= ceiling 100000; nsif_emp=8%*50000=4000, nsif_empr=17%*50000=8500
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["NSIF Employee"]["amount"], 4000, delta=1)
        self.assertAlmostEqual(r["NSIF Employer"]["amount"], 8500, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(50000))
        self.assertFalse(r["NSIF Employee"]["is_employer_only"])
        self.assertTrue(r["NSIF Employer"]["is_employer_only"])

    def test_nsif_ceiling(self):
        # gross=200000 > ceiling 100000; nsif_emp capped: 8%*100000=8000, nsif_empr: 17%*100000=17000
        r = self.calc.compute(slip(200000))
        self.assertAlmostEqual(r["NSIF Employee"]["amount"], 8000, delta=1)
        self.assertAlmostEqual(r["NSIF Employer"]["amount"], 17000, delta=1)

    def test_below_pit_threshold(self):
        # PIT threshold annual=120000; gross=8000:
        # nsif_emp=8%*8000=640, taxable=7360, annual=88320 < 120000 => no PIT
        r = self.calc.compute(slip(8000))
        self.assertNotIn("PIT", r)



class TestAlgeriaExtraBands(unittest.TestCase):
    """Tests for Algeria pit_bands reading from settings."""

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.algeria import AlgeriaCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        # Simple 2-band slab: 0-500000 @ 0%, 500000+ @ 10% (annual)
        calc = AlgeriaCalculator(MockSettings(
            cnas_employee_rate=9, cnas_employer_rate=26,
            pit_bands=[Band(0, 500000, 0), Band(500000, 0, 10)],
        ))
        # gross=60000/month; cnas_emp=5400; taxable=54600; annual=655200
        # band tax: (655200-500000)*10% = 15520; monthly = 1293.33
        r = calc.compute(slip(60000))
        self.assertAlmostEqual(r["PIT"]["amount"], 1293.33, delta=2)

    def test_empty_pit_bands_uses_hardcoded(self):
        from payroll_africa.calculators.algeria import AlgeriaCalculator
        calc = AlgeriaCalculator(MockSettings(cnas_employee_rate=9, cnas_employer_rate=26))
        # gross=25000: cnas_emp=2250; taxable=22750; annual=273000 > 240000 → 23% bracket
        r = calc.compute(slip(25000))
        self.assertIn("PIT", r)
        self.assertGreater(r["PIT"]["amount"], 0)


class TestLibyaExtraBands(unittest.TestCase):
    """Tests for Libya pit_bands and solidarity_fund_rate from settings."""

    def test_solidarity_reads_from_settings(self):
        from payroll_africa.calculators.libya import LibyaCalculator
        calc = LibyaCalculator(MockSettings(
            ssf_employee_rate=5.125, ssf_employer_rate=14.35, solidarity_fund_rate=2,
        ))
        r = calc.compute(slip(1000))
        # solidarity = 2% of 1000 = 20
        self.assertAlmostEqual(r["Solidarity Fund"]["amount"], 20, delta=0.01)

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.libya import LibyaCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = LibyaCalculator(MockSettings(
            ssf_employee_rate=5.125, ssf_employer_rate=14.35, solidarity_fund_rate=1,
            pit_bands=[Band(0, 12000, 5), Band(12000, 0, 10)],
        ))
        # gross=5000: ssf_emp=256.25, sol=50; taxable=4693.75; annual=56325
        # tax: 12000*5% + (56325-12000)*10% = 600 + 4432.5 = 5032.5; monthly=419.375
        r = calc.compute(slip(5000))
        self.assertAlmostEqual(r["PIT"]["amount"], 419.375, delta=2)

    def test_empty_pit_bands_uses_hardcoded(self):
        from payroll_africa.calculators.libya import LibyaCalculator
        calc = LibyaCalculator(MockSettings(
            ssf_employee_rate=5.125, ssf_employer_rate=14.35, solidarity_fund_rate=1,
        ))
        # gross=5000: PIT > 0 with hardcoded bands
        r = calc.compute(slip(5000))
        self.assertIn("PIT", r)
        self.assertGreater(r["PIT"]["amount"], 0)


class TestComorosExtraBands(unittest.TestCase):
    """Tests for Comoros pit_bands and pit_threshold from settings."""

    def test_pit_reads_bands_from_settings(self):
        from payroll_africa.calculators.comoros import ComorosCalculator
        class Band:
            def __init__(self, f, t, r): self.from_amount = f; self.to_amount = t; self.rate = r
        calc = ComorosCalculator(MockSettings(
            minimum_wage=55000, cnss_employee_rate=3.5, cnss_employer_rate=10.5,
            pit_bands=[Band(0, 360000, 0), Band(360000, 0, 10)],
        ))
        # gross=50000; ceiling=55000*8=440000; cnss_emp=1750; taxable=48250; annual=579000
        # tax: (579000-360000)*10% = 21900; monthly = 1825
        r = calc.compute(slip(50000))
        self.assertAlmostEqual(r["PIT"]["amount"], 1825, delta=2)

    def test_empty_pit_bands_uses_hardcoded_with_threshold(self):
        from payroll_africa.calculators.comoros import ComorosCalculator
        calc = ComorosCalculator(MockSettings(
            minimum_wage=55000, cnss_employee_rate=3.5, cnss_employer_rate=10.5,
            pit_threshold=360000,
        ))
        r = calc.compute(slip(25000))
        self.assertNotIn("PIT", r)


class TestSeychelles(unittest.TestCase):
    """Seychelles calculator tests — PAYE + Social Security."""

    def setUp(self):
        from payroll_africa.calculators.seychelles import SeychellesCalculator
        self.calc = SeychellesCalculator(MockSettings(
            social_security_rate=5, social_security_ceiling=15000,
            tax_free_threshold=8555.5,
        ))

    def test_below_threshold_no_paye(self):
        r = self.calc.compute(slip(8000))
        self.assertNotIn("PAYE", r)
        self.assertIn("Social Security Employer", r)

    def test_paye_first_band(self):
        # gross=9000; PAYE: (9000-8555.5)*15% = 444.5*15% = 66.675
        r = self.calc.compute(slip(9000))
        self.assertAlmostEqual(r["PAYE"]["amount"], 66.675, delta=0.01)
        self.assertFalse(r["PAYE"]["is_employer_only"])

    def test_social_security_capped(self):
        # gross=20000 > ceiling 15000; SS = 15000 * 5% = 750
        r = self.calc.compute(slip(20000))
        self.assertAlmostEqual(r["Social Security Employer"]["amount"], 750, delta=1)
        self.assertTrue(r["Social Security Employer"]["is_employer_only"])

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["Social Security Employer"]["amount"], 0, delta=0.01)
        self.assertNotIn("PAYE", r)

    def test_paye_reads_bands_from_settings(self):
        from payroll_africa.calculators.seychelles import SeychellesCalculator
        class Band:
            def __init__(self, f, t, r):
                self.from_amount = f; self.to_amount = t; self.rate = r
        # Settings bands are monthly (child DocType field is `rate`)
        calc = SeychellesCalculator(MockSettings(
            social_security_rate=5, social_security_ceiling=15000,
            tax_free_threshold=8555.5,
            paye_bands=[Band(0, 8555.5, 0), Band(8555.5, 0, 10)],
        ))
        # gross=9000: (9000-8555.5)*10% = 44.45
        r = calc.compute(slip(9000))
        self.assertAlmostEqual(r["PAYE"]["amount"], 44.45, delta=0.01)

    def test_paye_twenty_percent_band(self):
        # gross=50000: 15% x 1444.5 = 216.675; 20% x (50000-10000) = 8000 -> 8216.675
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["PAYE"]["amount"], 8216.675, delta=0.01)

    def test_paye_top_band_starts_at_83333(self):
        # gross=100000: 216.675 + 20% x 73333 (14666.6) + 30% x 16667 (5000.1) = 19883.375
        r = self.calc.compute(slip(100000))
        self.assertAlmostEqual(r["PAYE"]["amount"], 19883.375, delta=0.01)

    def test_paye_tax_free_threshold_from_settings(self):
        from payroll_africa.calculators.seychelles import SeychellesCalculator
        # Custom threshold of 10000 — gross=9500 should have no PAYE
        calc = SeychellesCalculator(MockSettings(
            social_security_rate=5, social_security_ceiling=15000,
            tax_free_threshold=10000,
        ))
        r = calc.compute(slip(9500))
        self.assertNotIn("PAYE", r)


class TestMauritius(unittest.TestCase):
    """Mauritius calculator tests — NSF, CSG, HRDC, PAYE."""

    def setUp(self):
        from payroll_africa.calculators.mauritius import MauritiusCalculator
        self.calc = MauritiusCalculator(MockSettings(
            nsf_employee_rate=1, nsf_employer_rate=2.5, nsf_ceiling=28570,
            csg_rate=1.5, hrdc_rate=1.5, prgf_rate=4.5,
            prgf_exemption_threshold=200000,
            exempt_threshold_monthly=38462,
            paye_bands=[],
        ))

    def test_nsf_below_ceiling(self):
        # gross=20000 < ceiling 28570; nsf_emp=1%*20000=200, nsf_empr=2.5%*20000=500
        r = self.calc.compute(slip(20000))
        self.assertAlmostEqual(r["NSF Employee"]["amount"], 200, delta=1)
        self.assertAlmostEqual(r["NSF Employer"]["amount"], 500, delta=1)

    def test_nsf_above_ceiling(self):
        # gross=50000 > ceiling 28570; nsf_emp=1%*28570=285.70, nsf_empr=2.5%*28570=714.25
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["NSF Employee"]["amount"], 285.70, delta=1)
        self.assertAlmostEqual(r["NSF Employer"]["amount"], 714.25, delta=1)

    def test_csg_below_threshold(self):
        # gross=30000 <= csg_high_threshold 50000; csg=1.5%*30000=450
        r = self.calc.compute(slip(30000))
        self.assertAlmostEqual(r["CSG"]["amount"], 450, delta=1)
        self.assertFalse(r["CSG"]["is_employer_only"])

    def test_hrdc_levy(self):
        # hrdc=1.5%*30000=450
        r = self.calc.compute(slip(30000))
        self.assertAlmostEqual(r["HRDC Levy"]["amount"], 450, delta=1)
        self.assertTrue(r["HRDC Levy"]["is_employer_only"])

    def test_exempt_below_threshold(self):
        # gross=35000 < exempt_threshold 38462 => no PAYE
        r = self.calc.compute(slip(35000))
        self.assertNotIn("PAYE", r)

    def test_paye_above_exempt(self):
        # gross=50000 > 38462 => PAYE > 0
        r = self.calc.compute(slip(50000))
        self.assertIn("PAYE", r)
        self.assertGreater(r["PAYE"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["NSF Employee"]["amount"], 0, delta=0.01)
        self.assertAlmostEqual(r["NSF Employer"]["amount"], 0, delta=0.01)
        self.assertNotIn("PAYE", r)
        self.assertNotIn("CSG", r)


class TestDRC(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.drc import DRCCalculator
        self.calc = DRCCalculator(MockSettings(
            inss_pension_employee_rate=5,
            inss_pension_employer_rate=5,
            inss_occupational_risks_rate=1.5,
            inss_family_benefits_rate=6.5,
            inpp_rate=3,
            onem_rate=0.2,
        ))

    def test_inss_contributions(self):
        # gross=800000: INSS emp=5%*800000=40000, INSS empr=5%*800000=40000
        r = self.calc.compute(slip(800000))
        self.assertAlmostEqual(r["INSS Pension Employee CD"]["amount"], 40000, delta=1)
        self.assertAlmostEqual(r["INSS Pension Employer CD"]["amount"], 40000, delta=1)
        self.assertFalse(r["INSS Pension Employee CD"]["is_employer_only"])
        self.assertTrue(r["INSS Pension Employer CD"]["is_employer_only"])

    def test_employer_contributions(self):
        # gross=800000: occ_risk=1.5%*800000=12000, family=6.5%*800000=52000
        # inpp=3%*800000=24000, onem=0.2%*800000=1600
        r = self.calc.compute(slip(800000))
        self.assertAlmostEqual(r["INSS Occupational Risks CD"]["amount"], 12000, delta=1)
        self.assertAlmostEqual(r["INSS Family Benefits CD"]["amount"], 52000, delta=1)
        self.assertAlmostEqual(r["INPP CD"]["amount"], 24000, delta=1)
        self.assertAlmostEqual(r["ONEM CD"]["amount"], 1600, delta=1)

    def test_ipr_computed_from_bands(self):
        # gross=800000; inss_emp=40000; taxable=760000
        # Band1: 0-162000 at 3% => 162000*0.03 = 4860
        # Band2: 162001-1800000 at 15% => (760000-162001)*0.15 = 89699.85
        # Total IPR = 4860 + 89699.85 = 94559.85
        r = self.calc.compute(slip(800000))
        self.assertIn("PAYE CD", r)
        self.assertAlmostEqual(r["PAYE CD"]["amount"], 94559.85, delta=5)
        self.assertFalse(r["PAYE CD"]["is_employer_only"])

    def test_zero_gross_no_ipr(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["INSS Pension Employee CD"]["amount"], 0, delta=1)
        self.assertNotIn("PAYE CD", r)

    def test_fallback_rates_no_crash(self):
        # MockSettings with no rate fields: defaults must kick in
        from payroll_africa.calculators.drc import DRCCalculator
        calc_bare = DRCCalculator(MockSettings())
        r = calc_bare.compute(slip(500000))
        # Default inss_pension_employee=5% => 25000
        self.assertAlmostEqual(r["INSS Pension Employee CD"]["amount"], 25000, delta=1)
        self.assertIn("PAYE CD", r)

if __name__ == "__main__":
    unittest.main(verbosity=2)
