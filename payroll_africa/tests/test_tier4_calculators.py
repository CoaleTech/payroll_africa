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
        self.calc = AlgeriaCalculator(MockSettings(cnas_employee_rate=9, cnas_employer_rate=25.5))

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
        self.calc = LibyaCalculator(MockSettings(ssf_employee_rate=3.75, ssf_employer_rate=14.35))

    def test_ssf_solidarity_jehad(self):
        r = self.calc.compute(slip(2000))
        self.assertAlmostEqual(r["SSF Employee"]["amount"], 75, delta=1)
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
        # gross=2000: ssf_emp=3.75%*2000=75, ssf_empr=14.35%*2000=287
        # solidarity=1%*2000=20, jehad=3%*2000=60
        r = self.calc.compute(slip(2000))
        self.assertAlmostEqual(r["SSF Employee"]["amount"], 75, delta=1)
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
        self.calc = EquatorialGuineaCalculator(MockSettings(minimum_wage=150000, cnss_employee_rate=4.5, cnss_employer_rate=21.5))

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
        self.calc = DjiboutiCalculator(MockSettings(minimum_wage=45000, cnss_employee_rate=4, cnss_employer_rate=12))

    def test_cnss(self):
        r = self.calc.compute(slip(400000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # ceiling = 45000 * 8 = 360000; gross 200000 below ceiling
        # CNSS emp: 200000 * 4% = 8,000; empr: 200000 * 12% = 24,000
        r = self.calc.compute(slip(200000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 8000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 24000, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(200000))
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross 500000 > ceiling 360000; CNSS emp = 360000 * 4% = 14,400
        r = self.calc.compute(slip(500000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 14400, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 43200, delta=1)

    def test_below_pit_threshold(self):
        # annual PIT threshold 600,000; gross 40000: taxable ~38400, annual ~460800 < 600000
        r = self.calc.compute(slip(40000))
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
        # annual PIT threshold 18,000; gross 1000: taxable ~950, annual ~11400 < 18000
        r = self.calc.compute(slip(1000))
        self.assertNotIn("PIT", r)


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
        self.calc = ComorosCalculator(MockSettings(minimum_wage=75000, cnss_employee_rate=3.5, cnss_employer_rate=10.5))

    def test_cnss(self):
        r = self.calc.compute(slip(700000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 0, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 0, delta=1)
        self.assertNotIn("PIT", r)

    def test_key_components(self):
        # ceiling = 75000 * 8 = 600000; gross 300000 below ceiling
        # CNSS emp: 300000 * 3.5% = 10,500; empr: 300000 * 10.5% = 31,500
        r = self.calc.compute(slip(300000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 10500, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 31500, delta=1)

    def test_employer_only_flag(self):
        r = self.calc.compute(slip(300000))
        self.assertFalse(r["CNSS Employee"]["is_employer_only"])
        self.assertTrue(r["CNSS Employer"]["is_employer_only"])

    def test_ceiling(self):
        # gross 800000 > ceiling 600000; CNSS emp = 600000 * 3.5% = 21,000
        r = self.calc.compute(slip(800000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 21000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 63000, delta=1)

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
        self.calc = CaboVerdeCalculator(MockSettings(inps_ceiling=80000, inps_employee_rate=8.5, inps_employer_rate=16, work_injury_risk=1))

    def test_inps_injury(self):
        r = self.calc.compute(slip(100000))
        # INPS capped at 80k: emp 8.5% = 6,800
        self.assertAlmostEqual(r["INPS Employee"]["amount"], 6800, delta=1)
        # Injury: 2% of 100k = 2,000
        self.assertAlmostEqual(r["Work Injury Insurance"]["amount"], 2000, delta=1)
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
        # annual taxable ~274,500 < 300,000 threshold: no PIT
        r = self.calc.compute(slip(25000))
        self.assertNotIn("PIT", r)


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
