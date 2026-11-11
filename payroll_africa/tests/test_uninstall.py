"""Regression tests for payroll_africa.setup before_uninstall helpers.

These tests verify the uninstall custom-field list WITHOUT touching the
database. Salary Structures, Components and Income Tax Slabs are removed via
_remove_country_assets, which derives them from each country's setup, so they
need no hand-maintained list.
"""

import unittest

from payroll_africa.setup import _remove_custom_fields


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


if __name__ == "__main__":
    unittest.main()
