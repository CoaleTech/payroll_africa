"""Tests for SOUTH group statutory corrections: Guinea, Namibia, Eswatini, Lesotho, Zimbabwe.
"""
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Minimal frappe stub — must happen before any app import
# ---------------------------------------------------------------------------
_frappe = MagicMock()


def _mock_flt(value, precision=None):
    if value is None:
        return 0.0
    return float(value)


_frappe.utils.flt = _mock_flt
_frappe.utils.getdate = MagicMock(side_effect=lambda x: x)
sys.modules.setdefault("frappe", _frappe)
sys.modules.setdefault("frappe.utils", _frappe.utils)

from payroll_africa.calculators.guinea import GuineaCalculator  # noqa: E402
from payroll_africa.calculators.namibia import NamibiaCalculator  # noqa: E402
from payroll_africa.calculators.eswatini import EswatiniCalculator  # noqa: E402
from payroll_africa.calculators.lesotho import LesothoCalculator  # noqa: E402
from payroll_africa.calculators.zimbabwe import ZimbabweCalculator  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _slip(gross):
    s = MagicMock()
    s.gross_pay = gross
    s.earnings = []
    s.employee = "EMP-001"
    s.end_date = None
    return s


def _amt(results, key):
    return round(results[key]["amount"], 2)


# ===========================================================================
# GUINEA
# ===========================================================================
class TestGuineaCalculator(unittest.TestCase):

    def _make_settings(self, **kw):
        s = MagicMock()
        s.inss_pension_employee_rate = kw.get("inss_pension_employee_rate", 5)
        s.inss_pension_employer_rate = kw.get("inss_pension_employer_rate", 1.5)
        s.inss_family_rate = kw.get("inss_family_rate", 6)
        s.work_injury_risk_class = kw.get("work_injury_risk_class", 1)
        s.amo_employee_rate = kw.get("amo_employee_rate", 0)
        s.amo_employer_rate = kw.get("amo_employer_rate", 6.5)
        s.minimum_wage = kw.get("minimum_wage", 550000)
        s.inss_ceiling = kw.get("inss_ceiling", 2500000)
        s.pit_bands = kw.get("pit_bands", [])
        return s

    def test_pension_rates(self):
        """Employee 5%, Employer 1.5% on capped base."""
        calc = GuineaCalculator(self._make_settings())
        results = calc.compute(_slip(500000))
        # Base = min(500k, 2.5M) = 500k
        self.assertAlmostEqual(_amt(results, "INSS Pension Employee"), 25000, places=0)
        self.assertAlmostEqual(_amt(results, "INSS Pension Employer"), 7500, places=0)

    def test_family_rate(self):
        """Family allowances employer 6%."""
        calc = GuineaCalculator(self._make_settings())
        results = calc.compute(_slip(500000))
        self.assertAlmostEqual(_amt(results, "INSS Family Allowances"), 30000, places=0)

    def test_work_injury_flat_4pct(self):
        """Work injury always 4% regardless of risk class."""
        for risk_class in (1, 2, 3):
            with self.subTest(risk_class=risk_class):
                calc = GuineaCalculator(self._make_settings(work_injury_risk_class=risk_class))
                results = calc.compute(_slip(500000))
                self.assertAlmostEqual(_amt(results, "Work Injury Insurance"), 20000, places=0)

    def test_amo_rates(self):
        """AMO employee 0%, employer 6.5%."""
        calc = GuineaCalculator(self._make_settings())
        results = calc.compute(_slip(500000))
        self.assertAlmostEqual(_amt(results, "AMO Health Employee"), 0.0, places=2)
        self.assertAlmostEqual(_amt(results, "AMO Health Employer"), 32500, places=0)

    def test_ceiling_fixed_2500000(self):
        """Ceiling is the fixed inss_ceiling, not 8 × minimum_wage."""
        calc = GuineaCalculator(self._make_settings())
        results = calc.compute(_slip(5000000))  # gross > ceiling
        # Base = 2,500,000
        self.assertAlmostEqual(_amt(results, "INSS Pension Employee"), 125000, places=0)
        self.assertAlmostEqual(_amt(results, "Work Injury Insurance"), 100000, places=0)

    def test_minimum_wage_fallback_is_550000(self):
        """When inss_ceiling is unset, fallback is 2,500,000 (not 8 × 80,000 = 640,000)."""
        s = self._make_settings()
        s.inss_ceiling = 0  # triggers fallback
        calc = GuineaCalculator(s)
        results = calc.compute(_slip(5000000))
        # fallback ceiling = 2,500,000 → pension_emp = 5% × 2.5M = 125,000
        self.assertAlmostEqual(_amt(results, "INSS Pension Employee"), 125000, places=0)

    def test_pit_zero_below_threshold(self):
        """No PIT key when gross < 100,000 GNF/month (annual < 1,200,000)."""
        calc = GuineaCalculator(self._make_settings())
        results = calc.compute(_slip(90000))
        self.assertNotIn("PIT", results)

    def test_pit_at_500000_gross(self):
        """PIT at gross 500,000: taxable 475,000, annual 5.7M → PIT = 34,500/month."""
        calc = GuineaCalculator(self._make_settings())
        results = calc.compute(_slip(500000))
        # taxable = 500,000 - 25,000 (pension) - 0 (AMO) = 475,000
        # annual = 5,700,000
        # 1.8M * 5% + 2.7M * 12% = 90,000 + 324,000 = 414,000 / 12 = 34,500
        self.assertAlmostEqual(_amt(results, "PIT"), 34500, places=0)

    def test_zero_gross(self):
        """All amounts zero at gross = 0."""
        calc = GuineaCalculator(self._make_settings())
        results = calc.compute(_slip(0))
        self.assertEqual(_amt(results, "INSS Pension Employee"), 0)
        self.assertEqual(_amt(results, "Work Injury Insurance"), 0)
        self.assertNotIn("PIT", results)


# ===========================================================================
# NAMIBIA
# ===========================================================================
class TestNamibiaSSCCeiling2026(unittest.TestCase):

    def _make_settings(self, ceiling=150000):
        s = MagicMock()
        s.ssc_annual_ceiling = ceiling
        s.ssc_rate = 0.9
        s.vet_levy_applicable = 1
        s.vet_levy_rate = 1
        s.ecf_risk_sector = "low"
        s.paye_bands = []
        return s

    def test_ssc_capped_at_150000(self):
        """SSC capped at NAD 150,000/year = 12,500/month → max per side = 112.50."""
        calc = NamibiaCalculator(self._make_settings(150000))
        results = calc.compute(_slip(15000))
        self.assertAlmostEqual(_amt(results, "Social Security Employee"), 112.50, places=2)
        self.assertAlmostEqual(_amt(results, "Social Security Employer"), 112.50, places=2)

    def test_ssc_below_cap(self):
        """SSC uncapped at low gross: 0.9% of gross."""
        calc = NamibiaCalculator(self._make_settings(150000))
        results = calc.compute(_slip(5000))
        self.assertAlmostEqual(_amt(results, "Social Security Employee"), 45.0, places=2)

    def test_paye_new_bands_300000_annual(self):
        """Annual 300,000: band 150k-350k@25%, base 9,000 → 9,000+150,000*25%=46,500/yr → 3,875/mo."""
        calc = NamibiaCalculator(self._make_settings())
        results = calc.compute(_slip(25000))  # 25,000 × 12 = 300,000
        self.assertAlmostEqual(_amt(results, "PAYE"), 3875.0, places=0)

    def test_paye_hardcoded_boundary_100k(self):
        """Annual income ≤ 100,000 → PAYE = 0."""
        calc = NamibiaCalculator(self._make_settings())
        results = calc.compute(_slip(8000))  # 8,000 × 12 = 96,000
        self.assertAlmostEqual(_amt(results, "PAYE"), 0.0, places=2)

    def test_paye_hardcoded_band2_150k(self):
        """Annual 150,000: 50,000 × 18% = 9,000/yr → 750/mo."""
        calc = NamibiaCalculator(self._make_settings())
        results = calc.compute(_slip(12500))  # 12,500 × 12 = 150,000
        self.assertAlmostEqual(_amt(results, "PAYE"), 750.0, places=1)

    def test_paye_seeded_bands_formula(self):
        """Band formula with new seeded bands for gross = 25,000 (annual 300,000)."""
        s = self._make_settings()
        s.paye_bands = [
            SimpleNamespace(from_amount=0, to_amount=100000, rate=0, base_tax=0),
            SimpleNamespace(from_amount=100001, to_amount=150000, rate=18, base_tax=0),
            SimpleNamespace(from_amount=150001, to_amount=350000, rate=25, base_tax=9000),
            SimpleNamespace(from_amount=350001, to_amount=550000, rate=28, base_tax=59000),
            SimpleNamespace(from_amount=550001, to_amount=850000, rate=30, base_tax=115000),
            SimpleNamespace(from_amount=850001, to_amount=1550000, rate=32, base_tax=205000),
            SimpleNamespace(from_amount=1550001, to_amount=0, rate=37, base_tax=429000),
        ]
        calc = NamibiaCalculator(s)
        results = calc.compute(_slip(25000))
        # annual=300,000; band150k-350k: 9,000+(300,000-150,001)*25%=9,000+37,499.75=46,499.75
        self.assertAlmostEqual(_amt(results, "PAYE"), 46499.75 / 12, places=1)

    def test_paye_high_band_1550k_plus(self):
        """Annual > 1,550,000 → top band 37%."""
        calc = NamibiaCalculator(self._make_settings())
        # gross 140,000 → annual 1,680,000
        # 429,000 + (1,680,000 - 1,550,000) * 37% = 429,000 + 48,100 = 477,100/yr
        results = calc.compute(_slip(140000))
        self.assertAlmostEqual(_amt(results, "PAYE"), 477100 / 12, places=0)


# ===========================================================================
# ESWATINI
# ===========================================================================
class TestEswatiniCalculator(unittest.TestCase):

    def _make_settings(self, cap=430, rebate_annual=8200, rebate_secondary=2700, sdl=1):
        s = MagicMock()
        s.enpf_cap_total = cap
        s.enpf_rate = 5
        s.tax_rebate_annual = rebate_annual
        s.tax_rebate_secondary = rebate_secondary
        s.sdl_rate = sdl
        s.paye_bands = []
        return s

    def test_enpf_cap_215_per_side(self):
        """ENPF cap E430 total → E215 per side; gross 5,000 → capped."""
        calc = EswatiniCalculator(self._make_settings(cap=430))
        with patch.object(calc, "get_employee_age", return_value=None):
            results = calc.compute(_slip(5000))
        self.assertAlmostEqual(_amt(results, "ENPF Employee"), 215.0, places=2)
        self.assertAlmostEqual(_amt(results, "ENPF Employer"), 215.0, places=2)

    def test_enpf_below_cap(self):
        """ENPF uncapped at low gross: 5% of 3,000 = 150 < 215."""
        calc = EswatiniCalculator(self._make_settings(cap=430))
        with patch.object(calc, "get_employee_age", return_value=None):
            results = calc.compute(_slip(3000))
        self.assertAlmostEqual(_amt(results, "ENPF Employee"), 150.0, places=2)

    def test_paye_primary_rebate_only(self):
        """PAYE with primary rebate only (no secondary) for gross 5,000."""
        calc = EswatiniCalculator(self._make_settings())
        with patch.object(calc, "get_employee_age", return_value=40):
            results = calc.compute(_slip(5000))
        # taxable = 5000-215=4785; annual=57420; raw=57420*20%=11484; net=11484-8200=3284; mo=273.67
        self.assertAlmostEqual(_amt(results, "PAYE"), 273.67, places=1)

    def test_secondary_rebate_age_60(self):
        """Employee aged 60 gets secondary rebate E2,700 on top of primary E8,200."""
        calc = EswatiniCalculator(self._make_settings())
        with patch.object(calc, "get_employee_age", return_value=60):
            results = calc.compute(_slip(5000))
        # taxable=4785; annual=57420; raw=11484; net=max(11484-8200-2700,0)=584; mo=48.67
        self.assertAlmostEqual(_amt(results, "PAYE"), 584 / 12, places=1)

    def test_secondary_rebate_age_59_no_extra(self):
        """Employee aged 59 gets only primary rebate."""
        calc = EswatiniCalculator(self._make_settings())
        with patch.object(calc, "get_employee_age", return_value=59):
            r1 = calc.compute(_slip(5000))
        with patch.object(calc, "get_employee_age", return_value=60):
            r2 = calc.compute(_slip(5000))
        self.assertGreater(_amt(r1, "PAYE"), _amt(r2, "PAYE"))

    def test_secondary_rebate_no_dob(self):
        """When DOB is missing (age=None), only primary rebate applies."""
        calc = EswatiniCalculator(self._make_settings())
        with patch.object(calc, "get_employee_age", return_value=None):
            results_none = calc.compute(_slip(5000))
        with patch.object(calc, "get_employee_age", return_value=40):
            results_40 = calc.compute(_slip(5000))
        self.assertAlmostEqual(
            _amt(results_none, "PAYE"), _amt(results_40, "PAYE"), places=2
        )

    def test_sdl_employer_only(self):
        """SDL is employer-only."""
        calc = EswatiniCalculator(self._make_settings(sdl=1))
        with patch.object(calc, "get_employee_age", return_value=None):
            results = calc.compute(_slip(10000))
        self.assertAlmostEqual(_amt(results, "Skills Development Levy"), 100.0, places=2)
        self.assertTrue(results["Skills Development Levy"]["is_employer_only"])


# ===========================================================================
# LESOTHO
# ===========================================================================
class TestLesothoTaxFreeThreshold(unittest.TestCase):

    def _make_settings(self, threshold=0, credit=11640):
        s = MagicMock()
        s.tax_free_threshold = threshold
        s.tax_credit_annual = credit
        return s

    def test_threshold_zero_taxes_all_incomes(self):
        """With threshold=0 no free-threshold exemption; low-income still pays (before credit)."""
        calc = LesothoCalculator(self._make_settings(threshold=0))
        results = calc.compute(_slip(5000))
        # annual=60,000; tax=60,000*20%=12,000; net=12,000-11,640=360; mo=30
        self.assertAlmostEqual(_amt(results, "PAYE"), 30.0, places=1)

    def test_old_threshold_21600_was_exempt(self):
        """Regression: old default 21600 would zero PAYE for annual ≤ 21600."""
        calc = LesothoCalculator(self._make_settings(threshold=21600))
        results = calc.compute(_slip(1800))  # annual=21,600
        self.assertNotIn("PAYE", results)  # old wrong behaviour

    def test_no_threshold_all_incomes_covered(self):
        """With correct threshold=0, even a tiny income (above credit) pays PAYE."""
        calc = LesothoCalculator(self._make_settings(threshold=0))
        results = calc.compute(_slip(5000))
        self.assertIn("PAYE", results)

    def test_credit_still_works(self):
        """Annual credit M11,640 still reduces tax for mid-income."""
        calc = LesothoCalculator(self._make_settings(threshold=0, credit=11640))
        results = calc.compute(_slip(10000))
        # annual=120,000; 74,040*20% + 45,960*30% = 14,808+13,788=28,596; net=28,596-11,640=16,956; mo=1413
        self.assertAlmostEqual(_amt(results, "PAYE"), 1413.0, places=0)


# ===========================================================================
# ZIMBABWE — no code change; verify existing behaviour still correct
# ===========================================================================
class TestZimbabweVerified(unittest.TestCase):

    def _make_settings(self):
        s = MagicMock()
        s.nssa_rate = 4.5
        s.nssa_annual_ceiling = 8400
        s.aids_levy_rate = 3
        s.tax_free_threshold = 0
        s.paye_bands = []
        return s

    def test_nssa_ceiling_8400(self):
        """NSSA ceiling USD 8,400/year = USD 700/month → max per side 31.50."""
        calc = ZimbabweCalculator(self._make_settings())
        results = calc.compute(_slip(1000))  # well above ceiling
        self.assertAlmostEqual(_amt(results, "NSSA Pension Employee"), 31.50, places=2)

    def test_tax_free_threshold_zero_first_band_zero(self):
        """tax_free_threshold=0 correct: PAYE band 0-100 is 0%; gross=50 → no PAYE key."""
        calc = ZimbabweCalculator(self._make_settings())
        results = calc.compute(_slip(50))  # below USD 100 first band → PAYE = 0
        # When PAYE is 0 the key is absent (calculator only adds it when paye > 0)
        self.assertNotIn("PAYE", results)

    def test_paye_500(self):
        """PAYE at USD 500: taxable=500-22.5=477.5; band 301-1000: 477.5*25%-35=84.38."""
        calc = ZimbabweCalculator(self._make_settings())
        results = calc.compute(_slip(500))
        self.assertAlmostEqual(_amt(results, "PAYE"), 84.38, places=1)

    def test_aids_levy_3pct_of_paye(self):
        """AIDS levy = 3% of PAYE."""
        calc = ZimbabweCalculator(self._make_settings())
        results = calc.compute(_slip(500))
        paye = results["PAYE"]["amount"]
        aids = results["AIDS Levy"]["amount"]
        self.assertAlmostEqual(aids, paye * 0.03, places=4)


if __name__ == "__main__":
    unittest.main()
