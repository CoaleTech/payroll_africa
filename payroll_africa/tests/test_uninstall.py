"""Regression tests for payroll_africa.setup before_uninstall helpers.

These tests verify completeness and correctness of the uninstall cleanup
functions WITHOUT touching the database — they inspect module-level constants
and mock frappe to guarantee that every artifact the app creates is
represented in the removal lists.
"""

import unittest

from payroll_africa.setup import (
    _PAYROLL_AFRICA_SALARY_COMPONENTS,
    _remove_custom_fields,
    _remove_income_tax_slabs,
    _remove_salary_structures,
    _safe_delete,
    before_uninstall,
)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _list_from_function(func, varname):
    """Return the string literals from the named list-literal local variable
    inside *func*.  Uses ast.Constant.value (Python 3.8+ compatible)."""
    import ast
    import inspect
    src = inspect.getsource(func)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == varname:
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        ]
    return []


# ---------------------------------------------------------------------------
# Custom field completeness
# ---------------------------------------------------------------------------

class TestUninstallCustomFieldCompleteness(unittest.TestCase):
    """_remove_custom_fields must list every field added by _setup_custom_fields."""

    @classmethod
    def setUpClass(cls):
        cls.fields = _list_from_function(_remove_custom_fields, "fields")

    def test_employee_payroll_country_present(self):
        self.assertIn("Employee-payroll_country", self.fields)

    def test_zambia_employee_fields_present(self):
        for f in [
            "Employee-zm_statutory_section",
            "Employee-zm_tpin",
            "Employee-zm_nrc",
            "Employee-zm_statutory_column",
            "Employee-zm_napsa_no",
            "Employee-zm_nhima_no",
        ]:
            self.assertIn(f, self.fields, f"Missing Zambia field: {f}")

    def test_salary_structure_assignment_fields_present(self):
        for f in [
            "Salary Structure Assignment-payroll_country",
            "Salary Structure Assignment-payroll_africa_section",
            "Salary Structure Assignment-payroll_africa_notes",
        ]:
            self.assertIn(f, self.fields, f"Missing SSA field: {f}")

    def test_salary_component_fields_present(self):
        for f in [
            "Salary Component-payroll_africa_section",
            "Salary Component-p9a_tax_deduction_card_type",
            "Salary Component-p10a_tax_deduction_card_type",
        ]:
            self.assertIn(f, self.fields, f"Missing SC field: {f}")

    def test_total_field_count(self):
        # 6 Employee (Kenya/shared) + 6 Employee (Zambia) + 3 Salary Component + 3 SSA = 18
        self.assertGreaterEqual(len(self.fields), 18)


# ---------------------------------------------------------------------------
# Salary structure completeness
# ---------------------------------------------------------------------------

class TestUninstallSalaryStructureCompleteness(unittest.TestCase):
    """_remove_salary_structures must cover all 44 templates the app creates."""

    @classmethod
    def setUpClass(cls):
        cls.templates = _list_from_function(_remove_salary_structures, "templates")

    def test_original_21_tier1_templates(self):
        for name in [
            "Kenya Payroll Template", "Uganda Payroll Template",
            "Tanzania Payroll Template", "Rwanda Payroll Template",
            "Burundi Payroll Template", "Zambia Payroll Template",
            "Malawi Payroll Template", "DRC Payroll Template",
            "Nigeria Payroll Template", "Mozambique Payroll Template",
            "Angola Payroll Template",
            "Ethiopia Payroll Template", "South Africa Payroll Template",
            "Egypt Payroll Template", "Ghana Payroll Template",
            "Botswana Payroll Template", "Morocco Payroll Template",
            "Tunisia Payroll Template", "Namibia Payroll Template",
            "Madagascar Payroll Template", "Ivory Coast Payroll Template",
        ]:
            self.assertIn(name, self.templates, f"Missing tier-1 template: {name}")

    def test_tier2_templates(self):
        for name in [
            "Algeria Payroll Template", "Libya Payroll Template",
            "Sudan Payroll Template", "Mauritania Payroll Template",
            "Djibouti Payroll Template", "Eritrea Payroll Template",
            "Comoros Payroll Template", "Sierra Leone Payroll Template",
            "Liberia Payroll Template", "Gambia Payroll Template",
            "Cabo Verde Payroll Template", "Mauritius Payroll Template",
            "Senegal Payroll Template", "Mali Payroll Template",
        ]:
            self.assertIn(name, self.templates, f"Missing tier-2 template: {name}")

    def test_tier3_templates(self):
        for name in [
            "Niger Payroll Template", "Burkina Faso Payroll Template",
            "Benin Payroll Template", "Togo Payroll Template",
            "Seychelles Payroll Template", "Lesotho Payroll Template",
            "Eswatini Payroll Template", "Guinea Payroll Template",
            "Guinea-Bissau Payroll Template",
        ]:
            self.assertIn(name, self.templates, f"Missing tier-3 template: {name}")


# ---------------------------------------------------------------------------
# Income tax slab completeness
# ---------------------------------------------------------------------------

class TestUninstallIncomeSlabCompleteness(unittest.TestCase):
    """_remove_income_tax_slabs must cover all 44 slabs the app creates."""

    @classmethod
    def setUpClass(cls):
        cls.slabs = _list_from_function(_remove_income_tax_slabs, "slabs")

    def test_original_21_slabs(self):
        for name in [
            "Kenya PAYE 2025", "Uganda PAYE 2025", "Tanzania PAYE 2025",
            "Rwanda PAYE 2025", "Burundi PAYE 2025", "Zambia PAYE 2025",
            "Malawi PAYE 2025", "DRC PAYE 2025", "Nigeria PAYE 2025",
            "Mozambique PAYE 2025", "Angola PAYE 2025",
            "Ethiopia PIT 2025", "South Africa PAYE 2025",
            "Egypt IT 2025", "Ghana PAYE 2025",
            "Botswana PAYE 2025", "Morocco IR 2025",
            "Tunisia IRPP 2025", "Namibia PAYE 2025",
            "Madagascar IRSA 2025", "Ivory Coast ITS 2025",
        ]:
            self.assertIn(name, self.slabs, f"Missing tier-1 slab: {name}")

    def test_tier2_slabs(self):
        for name in [
            "Algeria IRG 2024", "Libya PIT 2025", "Sudan PIT 2025",
            "Mauritania ITS 2026",
            "Djibouti PIT 2026", "Eritrea PAYE 2026", "Comoros PIT 2026",
            "Sierra Leone PAYE 2026", "Liberia PAYE 2026", "Gambia PIT 2026",
            "Cabo Verde IRPC 2026", "Mauritius PAYE 2026", "Senegal IR 2026",
            "Mali ITS 2025",
        ]:
            self.assertIn(name, self.slabs, f"Missing tier-2 slab: {name}")

    def test_tier3_slabs(self):
        for name in [
            "Niger ITS 2025", "Burkina Faso IUTS 2026",
            "Benin ITS 2026", "Togo IRPP 2026",
            "Seychelles PAYE 2026", "Lesotho PAYE 2026", "Eswatini PAYE 2026",
            "Guinea PIT 2026", "Guinea-Bissau IRPS 2026",
        ]:
            self.assertIn(name, self.slabs, f"Missing tier-3 slab: {name}")


# ---------------------------------------------------------------------------
# Salary component completeness
# ---------------------------------------------------------------------------

class TestUninstallSalaryComponentCompleteness(unittest.TestCase):
    """_PAYROLL_AFRICA_SALARY_COMPONENTS must contain every component the app creates."""

    def test_no_basic_salary(self):
        self.assertNotIn("Basic Salary", _PAYROLL_AFRICA_SALARY_COMPONENTS)

    def test_tier2_components_present(self):
        for name in [
            "CNAS Employee", "CNAS Employer",                      # Algeria
            "SSF Employee", "SSF Employer",                        # Libya
            "NSIF Employee", "NSIF Employer",                      # Sudan
            "CNAM Health Employee", "CNAM Health Employer",        # Mauritania
            "NICE Employee", "NICE Employer",                      # Eritrea
            "NASSIT Employee", "NASSIT Employer",                  # Sierra Leone
            "NASSCorp Employee", "NASSCorp Employer",              # Liberia
            "SSHFC Employee", "SSHFC Employer",                    # Gambia
            "INPS Employee", "INPS Employer",                      # Cabo Verde
            "NSF Employee", "NSF Employer",                        # Mauritius
            "IPRES Pension Employee", "IPRES Pension Employer",    # Senegal
            "AMO Health Employee", "AMO Health Employer",          # Senegal/Mali/Niger
            "CNSS Pension Employee", "CNSS Pension Employer",      # Niger/Burkina
            "INSS Pension Employee", "INSS Pension Employer",      # Mali/Guinea
            "INAM Employee", "INAM Employer",                      # Togo
            "ENPF Employee", "ENPF Employer",                      # Eswatini
            "INSS Family Allowances",                              # Guinea
            "INSS Employee", "INSS Employer",                      # Guinea-Bissau
        ]:
            self.assertIn(name, _PAYROLL_AFRICA_SALARY_COMPONENTS,
                          f"Missing tier-2+ component: {name}")

    def test_no_duplicates_in_component_list(self):
        seen = set()
        duplicates = []
        for name in _PAYROLL_AFRICA_SALARY_COMPONENTS:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        self.assertEqual(duplicates, [],
                         f"Duplicate entries in _PAYROLL_AFRICA_SALARY_COMPONENTS: {duplicates}")


# ---------------------------------------------------------------------------
# _safe_delete logic
# ---------------------------------------------------------------------------

class TestSafeDeleteLogic(unittest.TestCase):
    """_safe_delete must return True for absent docs and delegate correctly."""

    def test_returns_true_for_absent_doc(self):
        """When the document does not exist, _safe_delete returns True immediately."""
        import unittest.mock as mock
        with mock.patch("payroll_africa.setup.frappe") as mock_frappe:
            mock_frappe.db.exists.return_value = None
            result = _safe_delete("Salary Component", "NonExistent Component")
        self.assertTrue(result)
        mock_frappe.delete_doc.assert_not_called()

    def test_deletes_when_not_linked(self):
        """When no submitted slip references the component, it is deleted."""
        import unittest.mock as mock
        with mock.patch("payroll_africa.setup.frappe") as mock_frappe:
            mock_frappe.db.exists.return_value = "PAYE"
            mock_frappe.db.sql.return_value = []
            result = _safe_delete("Salary Component", "PAYE")
        self.assertTrue(result)
        mock_frappe.delete_doc.assert_called_once_with("Salary Component", "PAYE", force=True)

    def test_skips_when_linked_to_submitted_slip(self):
        """When a submitted Salary Slip references the component, deletion is skipped."""
        import unittest.mock as mock
        with mock.patch("payroll_africa.setup.frappe") as mock_frappe:
            mock_frappe.db.exists.return_value = "PAYE"
            mock_frappe.db.sql.return_value = [("1",)]
            result = _safe_delete("Salary Component", "PAYE")
        self.assertFalse(result)
        mock_frappe.delete_doc.assert_not_called()

    def test_salary_structure_uses_slip_count(self):
        """For Salary Structure, linkage is checked via Salary Slip docstatus=1 count."""
        import unittest.mock as mock
        with mock.patch("payroll_africa.setup.frappe") as mock_frappe:
            mock_frappe.db.exists.return_value = "Kenya Payroll Template"
            mock_frappe.db.count.return_value = 0
            result = _safe_delete("Salary Structure", "Kenya Payroll Template")
        self.assertTrue(result)
        mock_frappe.db.count.assert_called_once_with(
            "Salary Slip",
            {"salary_structure": "Kenya Payroll Template", "docstatus": 1},
        )

    def test_income_tax_slab_uses_structure_count(self):
        """For Income Tax Slab, linkage is checked via active Salary Structure count."""
        import unittest.mock as mock
        with mock.patch("payroll_africa.setup.frappe") as mock_frappe:
            mock_frappe.db.exists.return_value = "Kenya PAYE 2025"
            mock_frappe.db.count.return_value = 2
            result = _safe_delete("Income Tax Slab", "Kenya PAYE 2025")
        self.assertFalse(result)
        mock_frappe.delete_doc.assert_not_called()


# ---------------------------------------------------------------------------
# before_uninstall orchestration
# ---------------------------------------------------------------------------

class TestBeforeUninstallCallsAllHelpers(unittest.TestCase):
    """before_uninstall must call all six cleanup helpers."""

    def test_all_helpers_called(self):
        import unittest.mock as mock
        with (
            mock.patch("payroll_africa.setup._remove_desktop_icon") as m_icon,
            mock.patch("payroll_africa.setup._remove_salary_structures") as m_ss,
            mock.patch("payroll_africa.setup._remove_salary_components") as m_sc,
            mock.patch("payroll_africa.setup._remove_income_tax_slabs") as m_its,
            mock.patch("payroll_africa.setup._remove_custom_fields") as m_cf,
            mock.patch("payroll_africa.setup._remove_property_setters") as m_ps,
        ):
            before_uninstall()
        m_icon.assert_called_once()
        m_ss.assert_called_once()
        m_sc.assert_called_once()
        m_its.assert_called_once()
        m_cf.assert_called_once()
        m_ps.assert_called_once()


if __name__ == "__main__":
    unittest.main()
