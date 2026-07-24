# Adding a New Country

Payroll Africa is designed to be extended. Adding a country follows a consistent pattern.

## Steps

1. **Create the calculator** — `calculators/{snake}.py` extending `BaseCalculator`, implementing `compute()` and returning `{component: {amount, is_employer_only}}`.
2. **Create the Settings DocType** — `{country}_payroll_settings` (Single) with rate fields and a tax-band child table.
3. **Create the Band DocType** — `{country}_paye_band` or `{country}_pit_band` (child table: `from_amount`, `to_amount`, `rate`).
4. **Register** — add entries to `COUNTRY_MAP` and `SETTINGS_MAP` in `engine/registry.py`.
5. **Boot** — add `"Country Name": "enable_{snake}"` to `COUNTRY_FIELD_MAP` in `boot.py`.
6. **Settings toggle** — add an `enable_{snake}` Check field to `payroll_africa_settings.json`.
7. **Sidebar** — add the settings link to `workspace_sidebar/payroll_africa.json`.
8. **Reports** — create the tax-return and social-security remittance reports under `payroll_africa/report/`.
9. **Tests** — add a test class covering zero gross, a rate spot-check, employer flags, ceilings, and PIT thresholds.
10. **Migrate** — run a site migration to install the new DocTypes.

## The calculator pattern

Each country implements `BaseCalculator`:

```python
class KenyaCalculator(BaseCalculator):
    def compute(self, salary_slip) -> dict:
        gross = self.get_gross_pay(salary_slip)
        results = {}

        nssf = self._compute_nssf(gross)
        results["NSSF Employee"] = {"amount": nssf["employee"], "is_employer_only": False}
        results["NSSF Employer"] = {"amount": nssf["employer"], "is_employer_only": True}
        # ... SHIF, Housing Levy, NITA ...

        return results
```

The registry maps country names to calculator classes and loads their settings:

```python
# engine/registry.py
COUNTRY_MAP = {
    "Kenya":  "payroll_africa.calculators.kenya.KenyaCalculator",
    "Senegal": "payroll_africa.calculators.senegal.SenegalCalculator",
    # ... 54 entries
}
```

Calculators fall back to hardcoded statutory defaults when the Settings DocType is empty, so payroll runs correctly out of the box.

## Testing

Run the suite before submitting:

```bash
bench --site your-site.local run-tests --app payroll_africa
```

Every country (except the documented Somalia/South Sudan no-ops) is covered by unit tests.
