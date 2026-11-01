"""Statutory correction tests for NORTH group: Algeria, Libya, Comoros, Mauritania.

Sources:
- Algeria CNAS employer 25%: CLEISS 2024 (cleiss.fr/docs/cotisations/algerie.html)
- Libya Jehad Tax abolished: EY Tax News Update 2025-1651 + Orbitax (14 Jul 2025)
- Comoros: no code change; single-source only (afrotools / CGI 2023)
- Mauritania: verified correct; no code change
"""
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, '/mnt/agents/output')

frappe_mock = MagicMock()
frappe_mock.utils = MagicMock()
frappe_mock.utils.flt = lambda v, p=None: float(v) if v is not None else 0.0
sys.modules.setdefault('frappe', frappe_mock)
sys.modules.setdefault('frappe.utils', frappe_mock.utils)


class MockSettings:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
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


# ---------------------------------------------------------------------------
# Algeria — CNAS employer rate corrected to 25 % (CLEISS 2024)
# ---------------------------------------------------------------------------

class TestAlgeriaCNASEmployer25(unittest.TestCase):
    """Verify the corrected 25 % CNAS employer rate (was 26 %)."""

    def setUp(self):
        from payroll_africa.calculators.algeria import AlgeriaCalculator
        # Explicit settings at new rate
        self.calc25 = AlgeriaCalculator(
            MockSettings(cnas_employee_rate=9, cnas_employer_rate=25)
        )
        # Fallback path: no explicit rate in settings — must default to 25
        self.calc_fallback = AlgeriaCalculator(MockSettings(cnas_employee_rate=None, cnas_employer_rate=None))

    def test_employer_rate_25_explicit(self):
        r = self.calc25.compute(slip(100000))
        self.assertAlmostEqual(r["CNAS Employer"]["amount"], 25000, delta=1)

    def test_employer_rate_25_fallback(self):
        # When no cnas_employer_rate is saved, fallback default must now be 25
        r = self.calc_fallback.compute(slip(100000))
        self.assertAlmostEqual(r["CNAS Employer"]["amount"], 25000, delta=1)

    def test_employer_rate_not_26(self):
        r = self.calc_fallback.compute(slip(100000))
        # Strict: not the old 26 % value
        self.assertNotAlmostEqual(r["CNAS Employer"]["amount"], 26000, delta=50)

    def test_employee_rate_unchanged_9pct(self):
        # Employee CNAS must remain 9 %
        r = self.calc25.compute(slip(50000))
        self.assertAlmostEqual(r["CNAS Employee"]["amount"], 4500, delta=1)

    def test_zero_gross(self):
        r = self.calc25.compute(slip(0))
        self.assertAlmostEqual(r["CNAS Employee"]["amount"], 0, delta=0)
        self.assertAlmostEqual(r["CNAS Employer"]["amount"], 0, delta=0)
        self.assertNotIn("PIT", r)

    def test_boundary_below_pit_threshold(self):
        # Taxable = 20000*0.91 = 18200/month, annual = 218400 < 240000 => no PIT
        r = self.calc25.compute(slip(20000))
        self.assertNotIn("PIT", r)

    def test_employer_is_employer_only(self):
        r = self.calc25.compute(slip(40000))
        self.assertTrue(r["CNAS Employer"]["is_employer_only"])
        self.assertFalse(r["CNAS Employee"]["is_employer_only"])


# ---------------------------------------------------------------------------
# Libya — Jehad Tax abolished 14 July 2025
# ---------------------------------------------------------------------------

class TestLibyaJehadTaxAbsent(unittest.TestCase):
    """Jehad Tax must never appear in LibyaCalculator results."""

    def setUp(self):
        from payroll_africa.calculators.libya import LibyaCalculator
        self.calc = LibyaCalculator(
            MockSettings(ssf_employee_rate=5.125, ssf_employer_rate=14.35, solidarity_fund_rate=1)
        )

    def _no_jehad(self, gross):
        r = self.calc.compute(slip(gross))
        self.assertNotIn("Jehad Tax", r, f"Jehad Tax must not appear for gross={gross}")

    def test_no_jehad_low_gross(self):
        self._no_jehad(40)      # was 1% band

    def test_no_jehad_mid_gross(self):
        self._no_jehad(75)      # was 2% band

    def test_no_jehad_high_gross(self):
        self._no_jehad(200)     # was 3% band

    def test_no_jehad_realistic_salary(self):
        self._no_jehad(2000)    # typical salary

    def test_ssf_solidarity_still_computed(self):
        r = self.calc.compute(slip(2000))
        self.assertAlmostEqual(r["SSF Employee"]["amount"], 102.5, delta=1)
        self.assertAlmostEqual(r["SSF Employer"]["amount"], 287.0, delta=1)
        self.assertAlmostEqual(r["Solidarity Fund"]["amount"], 20.0, delta=1)

    def test_ssf_employer_only_flag(self):
        r = self.calc.compute(slip(2000))
        self.assertTrue(r["SSF Employer"]["is_employer_only"])
        self.assertFalse(r["SSF Employee"]["is_employer_only"])
        self.assertFalse(r["Solidarity Fund"]["is_employer_only"])

    def test_zero_gross(self):
        r = self.calc.compute(slip(0))
        self.assertAlmostEqual(r["SSF Employee"]["amount"], 0, delta=0)
        self.assertAlmostEqual(r["SSF Employer"]["amount"], 0, delta=0)
        self.assertNotIn("PIT", r)
        self.assertNotIn("Jehad Tax", r)

    def test_pit_still_computed(self):
        # gross=5000: ssf_emp=256.25, sol=50; taxable=4693.75
        # annual=56325; PIT = 12000*5%+(56325-12000)*10% = 5032.5/12 = 419.4
        r = self.calc.compute(slip(5000))
        self.assertIn("PIT", r)
        self.assertAlmostEqual(r["PIT"]["amount"], 419.4, delta=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
