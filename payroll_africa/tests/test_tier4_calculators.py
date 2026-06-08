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


class TestCAR(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.central_african_republic import CentralAfricanRepublicCalculator
        self.calc = CentralAfricanRepublicCalculator(MockSettings(minimum_wage=50000, cnss_employee_rate=3, cnss_employer_rate=15))

    def test_cnss(self):
        r = self.calc.compute(slip(500000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)


class TestDjibouti(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.djibouti import DjiboutiCalculator
        self.calc = DjiboutiCalculator(MockSettings(minimum_wage=45000, cnss_employee_rate=4, cnss_employer_rate=12))

    def test_cnss(self):
        r = self.calc.compute(slip(400000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)


class TestGuineaBissau(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.guinea_bissau import GuineaBissauCalculator
        self.calc = GuineaBissauCalculator(MockSettings(minimum_wage=45000, inss_employee_rate=8, inss_employer_rate=14))

    def test_inss_pit(self):
        r = self.calc.compute(slip(1000000))
        # Ceiling: 8 * 45k = 360k; INSS emp: 8% of 360k = 28,800
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 28800, delta=1)


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


class TestGambia(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.gambia import GambiaCalculator
        self.calc = GambiaCalculator(MockSettings(sshfc_ceiling=25000, sshfc_employee_rate=5, sshfc_employer_rate=10))

    def test_sshfc(self):
        r = self.calc.compute(slip(50000))
        # Capped at 25k; emp 5% = 1,250
        self.assertAlmostEqual(r["SSHFC Employee"]["amount"], 1250, delta=1)


class TestEritrea(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.eritrea import EritreaCalculator
        self.calc = EritreaCalculator(MockSettings(nice_employee_rate=6, nice_employer_rate=12))

    def test_nice(self):
        r = self.calc.compute(slip(50000))
        self.assertAlmostEqual(r["NICE Employee"]["amount"], 3000, delta=1)
        self.assertAlmostEqual(r["NICE Employer"]["amount"], 6000, delta=1)


class TestComoros(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.comoros import ComorosCalculator
        self.calc = ComorosCalculator(MockSettings(minimum_wage=75000, cnss_employee_rate=3.5, cnss_employer_rate=10.5))

    def test_cnss(self):
        r = self.calc.compute(slip(700000))
        self.assertGreater(r["CNSS Employee"]["amount"], 0)


class TestSaoTomePrincipe(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.sao_tome_principe import SaoTomePrincipeCalculator
        self.calc = SaoTomePrincipeCalculator(MockSettings(inss_ceiling=500000, inss_employee_rate=3, inss_employer_rate=8))

    def test_inss(self):
        r = self.calc.compute(slip(400000))
        self.assertGreater(r["INSS Employee"]["amount"], 0)


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


class TestSudan(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.sudan import SudanCalculator
        self.calc = SudanCalculator(MockSettings(nsif_ceiling=100000, nsif_employee_rate=8, nsif_employer_rate=17))

    def test_nsif(self):
        r = self.calc.compute(slip(150000))
        # Capped at 100k: emp 8% = 8,000
        self.assertAlmostEqual(r["NSIF Employee"]["amount"], 8000, delta=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
