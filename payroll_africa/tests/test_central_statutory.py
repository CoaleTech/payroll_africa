"""Statutory correction tests — Group CENTRAL.

Covers: Chad, Congo, Gabon, Senegal, CAR, Togo, Sao Tome and Principe.

Sources:
  Chad        — PwC 2024, Central Africa Tax Guide 2023
  Congo       — PwC 2025 (CNSS 20.285%, ceiling 1,200,000, CAMU 0.5%)
  Gabon       — post-reform 2026 (CNSS employee 5%, employer 18%)
  Senegal     — CLEISS 2026 (AMO ceiling 250,000 XOF)
  CAR         — Sage 2025 / Africa HR Solutions (employer 19%, ceiling 600,000)
  Togo        — CLEISS 2026, CNSS Togo FAQ, auditcomtogo.com (no legal ceiling)
  Sao Tome    — Decree-Law 1/2025 (INSS employee 5%, employer 7%)
"""

import unittest
from unittest.mock import MagicMock
import sys

# Frappe mock — mirrors what the other test files do.
frappe_mock = MagicMock()
frappe_mock.utils = MagicMock()
frappe_mock.utils.flt = lambda v, p=None: float(v) if v is not None else 0.0
sys.modules.setdefault('frappe', frappe_mock)
sys.modules.setdefault('frappe.utils', frappe_mock.utils)

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


def slip(gross):
    s = MagicMock()
    s.gross_pay = gross
    s.earnings = []
    return s


# ---------------------------------------------------------------------------
# Chad — employer 5%, family 7.5%, ceiling 500,000 XAF
# ---------------------------------------------------------------------------
class TestChadStatutory(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.chad import ChadCalculator
        self.calc = ChadCalculator(MockSettings(
            cnps_ceiling=500000,
            cnps_pension_employee_rate=3.5,
            cnps_pension_employer_rate=5,
            family_allowances_rate=7.5,
            work_injury_risk_class=1,
        ))

    def test_employer_rate_is_five_percent(self):
        r = self.calc.compute(slip(500000))
        # base = min(500000, 500000) = 500000; employer = 5% of 500000 = 25,000
        self.assertAlmostEqual(r["CNPS Pension Employer"]["amount"], 25000, delta=1)

    def test_family_allowances_rate_is_seven_point_five(self):
        r = self.calc.compute(slip(300000))
        # base = 300000; 7.5% = 22,500
        self.assertAlmostEqual(r["CNPS Family Allowances"]["amount"], 22500, delta=1)

    def test_ceiling_500k(self):
        # Gross > ceiling: base capped at 500,000
        r = self.calc.compute(slip(1000000))
        self.assertAlmostEqual(r["CNPS Pension Employer"]["amount"], 25000, delta=1)
        self.assertAlmostEqual(r["CNPS Pension Employee"]["amount"], 17500, delta=1)

    def test_minimum_wage_fallback_builds_ceiling(self):
        from payroll_africa.calculators.chad import ChadCalculator
        # With no cnps_ceiling, ceiling = minimum_wage * 8 = 60000 * 8 = 480000
        calc = ChadCalculator(MockSettings(
            cnps_pension_employer_rate=5,
            family_allowances_rate=7.5,
            work_injury_risk_class=1,
        ))
        r = calc.compute(slip(600000))
        # base = min(600000, 480000) = 480000; employee 3.5% fallback * 480000 = 16800
        self.assertAlmostEqual(r["CNPS Pension Employee"]["amount"], 16800, delta=1)

    def test_below_ceiling_not_capped(self):
        r = self.calc.compute(slip(200000))
        # 200000 < 500000 ceiling; employer = 5% * 200000 = 10000
        self.assertAlmostEqual(r["CNPS Pension Employer"]["amount"], 10000, delta=1)


# ---------------------------------------------------------------------------
# Congo — CNSS employer 20.285%, employee 4%, ceiling 1,200,000, CAMU 0.5%
# ---------------------------------------------------------------------------
class TestCongoStatutory(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.congo import CongoCalculator
        self.calc = CongoCalculator(MockSettings(
            cnss_rate=20.285,
            cnss_employee_rate=4,
            cnss_ceiling=1200000,
            cnamgs_rate=0.5,
        ))

    def test_cnss_employer_rate(self):
        r = self.calc.compute(slip(500000))
        # 20.285% * 500000 = 101,425
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 101425, delta=1)

    def test_cnss_ceiling_1_2m(self):
        r = self.calc.compute(slip(2000000))
        # capped at 1,200,000; 20.285% * 1,200,000 = 243,420
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 243420, delta=1)

    def test_camu_rate_0_5(self):
        r = self.calc.compute(slip(1500000))
        # CAMU: 0.5% * (1,500,000 - 500,000) = 0.5% * 1,000,000 = 5,000
        self.assertAlmostEqual(r["CAMU Health Employer"]["amount"], 5000, delta=1)

    def test_camu_zero_below_500k(self):
        r = self.calc.compute(slip(400000))
        self.assertAlmostEqual(r["CAMU Health Employer"]["amount"], 0, delta=1)

    def test_cnss_employee_4pct_capped(self):
        r = self.calc.compute(slip(2000000))
        # 4% * 1,200,000 = 48,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 48000, delta=1)


# ---------------------------------------------------------------------------
# Gabon — post-reform: employee 5%, employer 18%
# ---------------------------------------------------------------------------
class TestGabonStatutory(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.gabon import GabonCalculator
        self.calc = GabonCalculator(MockSettings(
            use_2026_reform=1,
            cnss_employee_rate=5,
            cnss_employer_rate=18,
            cnss_ceiling=1500000,
            pit_threshold_annual=2160000,
        ))

    def test_employee_5pct(self):
        r = self.calc.compute(slip(1000000))
        # base = 1,000,000; employee 5% = 50,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 50000, delta=1)

    def test_employer_18pct(self):
        r = self.calc.compute(slip(1000000))
        # employer 18% = 180,000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 180000, delta=1)

    def test_ceiling_1_5m(self):
        r = self.calc.compute(slip(2000000))
        # capped at 1,500,000; employee 5% = 75,000; employer 18% = 270,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 75000, delta=1)
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 270000, delta=1)

    def test_pre_reform_fallback_16(self):
        from payroll_africa.calculators.gabon import GabonCalculator
        calc = GabonCalculator(MockSettings(
            use_2026_reform=0,
            cnss_ceiling=1500000,
        ))
        r = calc.compute(slip(500000))
        # pre-reform employee fallback 2.5% * 500000 = 12500
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 12500, delta=1)
        # pre-reform employer fallback 16% * 500000 = 80000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 80000, delta=1)


# ---------------------------------------------------------------------------
# Senegal — AMO ceiling 250,000 XOF
# ---------------------------------------------------------------------------
class TestSenegalAMOCeiling(unittest.TestCase):
    def test_amo_ceiling_250k(self):
        from payroll_africa.calculators.senegal import SenegalCalculator
        calc = SenegalCalculator(MockSettings(
            ipres_ceiling=432000, ipres_employee_rate=5.6, ipres_employer_rate=8.4,
            css_ceiling=432000, css_employee_rate=0, css_employer_rate=7,
            amo_applicable=1, amo_employee_rate=3, amo_employer_rate=3,
            amo_ceiling=None,  # None → fallback 250,000
            tax_free_threshold_annual=630000,
            child_deduction=100000, number_of_dependent_children=0,
            max_deductible_children=6,
        ))
        r = calc.compute(slip(400000))
        # AMO base = min(400000, 250000) = 250000; employee 3% = 7,500
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 7500, delta=1)

    def test_amo_ceiling_explicit_250k(self):
        from payroll_africa.calculators.senegal import SenegalCalculator
        calc = SenegalCalculator(MockSettings(
            ipres_ceiling=432000, ipres_employee_rate=5.6, ipres_employer_rate=8.4,
            css_ceiling=432000, css_employee_rate=0, css_employer_rate=7,
            amo_applicable=1, amo_employee_rate=3, amo_employer_rate=3,
            amo_ceiling=250000,
            tax_free_threshold_annual=630000,
            child_deduction=100000, number_of_dependent_children=0,
            max_deductible_children=6,
        ))
        r = calc.compute(slip(400000))
        # base = min(400000, 250000) = 250000; employee 3% = 7,500
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 7500, delta=1)
        # employer 3% = 7,500
        self.assertAlmostEqual(r["AMO Health Employer"]["amount"], 7500, delta=1)

    def test_amo_below_ceiling_uncapped(self):
        from payroll_africa.calculators.senegal import SenegalCalculator
        calc = SenegalCalculator(MockSettings(
            ipres_ceiling=432000, ipres_employee_rate=5.6, ipres_employer_rate=8.4,
            css_ceiling=432000, css_employee_rate=0, css_employer_rate=7,
            amo_applicable=1, amo_employee_rate=3, amo_employer_rate=3,
            amo_ceiling=250000,
            tax_free_threshold_annual=630000,
            child_deduction=100000, number_of_dependent_children=0,
            max_deductible_children=6,
        ))
        r = calc.compute(slip(200000))
        # 200000 < 250000 ceiling; base = 200000; employee 3% = 6,000
        self.assertAlmostEqual(r["AMO Health Employee"]["amount"], 6000, delta=1)


# ---------------------------------------------------------------------------
# CAR — employer 19%, fixed ceiling 600,000
# ---------------------------------------------------------------------------
class TestCARStatutory(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.central_african_republic import CentralAfricanRepublicCalculator
        self.calc = CentralAfricanRepublicCalculator(MockSettings(
            cnss_ceiling=600000,
            cnss_employee_rate=3,
            cnss_employer_rate=19,
        ))

    def test_employer_19pct(self):
        r = self.calc.compute(slip(400000))
        # base = 400000; 19% * 400000 = 76,000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 76000, delta=1)

    def test_employer_ceiling_600k(self):
        r = self.calc.compute(slip(900000))
        # capped at 600,000; 19% * 600000 = 114,000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 114000, delta=1)

    def test_employee_3pct(self):
        r = self.calc.compute(slip(400000))
        # 3% * 400000 = 12,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 12000, delta=1)

    def test_fallback_no_ceiling_uses_8x_min_wage(self):
        from payroll_africa.calculators.central_african_republic import CentralAfricanRepublicCalculator
        # No cnss_ceiling: ceiling = min_wage * 8 = 50000 * 8 = 400000
        calc = CentralAfricanRepublicCalculator(MockSettings(
            minimum_wage=50000,
            cnss_employee_rate=3,
            cnss_employer_rate=19,
        ))
        r = calc.compute(slip(600000))
        # base = min(600000, 400000) = 400000; 19% * 400000 = 76000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 76000, delta=1)


# ---------------------------------------------------------------------------
# Togo — no ceiling (cnss_ceiling = 0)
# ---------------------------------------------------------------------------
class TestTogoStatutory(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.togo import TogoCalculator
        self.calc = TogoCalculator(MockSettings(
            cnss_ceiling=0,
            cnss_employee_rate=4,
            cnss_employer_rate=17.5,
            inam_employee_rate=5,
            inam_employer_rate=5,
            pit_threshold=900000,
        ))

    def test_no_ceiling_high_gross(self):
        r = self.calc.compute(slip(2000000))
        # No cap; employee 4% * 2,000,000 = 80,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 80000, delta=1)
        # employer 17.5% * 2,000,000 = 350,000
        self.assertAlmostEqual(r["CNSS Employer"]["amount"], 350000, delta=1)

    def test_inam_uncapped(self):
        r = self.calc.compute(slip(1000000))
        # No cap; INAM employee 5% * 1,000,000 = 50,000
        self.assertAlmostEqual(r["INAM Employee"]["amount"], 50000, delta=1)

    def test_zero_ceiling_means_uncapped(self):
        # Boundary: a large salary should not be capped when ceiling=0
        r = self.calc.compute(slip(5000000))
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 200000, delta=1)  # 4% * 5M

    def test_positive_ceiling_still_caps(self):
        from payroll_africa.calculators.togo import TogoCalculator
        calc = TogoCalculator(MockSettings(
            cnss_ceiling=500000, cnss_employee_rate=4, cnss_employer_rate=17.5,
            inam_employee_rate=5, inam_employer_rate=5,
        ))
        r = calc.compute(slip(1000000))
        # capped at 500,000; employee 4% * 500000 = 20,000
        self.assertAlmostEqual(r["CNSS Employee"]["amount"], 20000, delta=1)


# ---------------------------------------------------------------------------
# Sao Tome and Principe — employee 5%, employer 7%
# ---------------------------------------------------------------------------
class TestSaoTomePrincipeStatutory(unittest.TestCase):
    def setUp(self):
        from payroll_africa.calculators.sao_tome_principe import SaoTomePrincipeCalculator
        self.calc = SaoTomePrincipeCalculator(MockSettings(
            inss_employee_rate=5,
            inss_employer_rate=7,
            inss_ceiling=500000,
        ))

    def test_employee_5pct(self):
        r = self.calc.compute(slip(300000))
        # 5% * 300000 = 15,000
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 15000, delta=1)

    def test_employer_7pct(self):
        r = self.calc.compute(slip(300000))
        # 7% * 300000 = 21,000
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 21000, delta=1)

    def test_ceiling_500k(self):
        r = self.calc.compute(slip(800000))
        # capped at 500000; employee 5% = 25,000; employer 7% = 35,000
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 25000, delta=1)
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 35000, delta=1)

    def test_default_fallbacks_5_7(self):
        from payroll_africa.calculators.sao_tome_principe import SaoTomePrincipeCalculator
        # No rates set: should fall back to 5% and 7%
        calc = SaoTomePrincipeCalculator(MockSettings(inss_ceiling=500000))
        r = calc.compute(slip(200000))
        self.assertAlmostEqual(r["INSS Employee"]["amount"], 10000, delta=1)  # 5%
        self.assertAlmostEqual(r["INSS Employer"]["amount"], 14000, delta=1)  # 7%

    def test_total_inss_12pct(self):
        r = self.calc.compute(slip(100000))
        emp = r["INSS Employee"]["amount"]
        empr = r["INSS Employer"]["amount"]
        # total = 12% of 100000 = 12,000
        self.assertAlmostEqual(emp + empr, 12000, delta=1)


if __name__ == "__main__":
    unittest.main()
