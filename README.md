<p align="center">
  <img src="payroll_africa/public/icons/desktop_icons/solid/payroll_africa.svg" alt="Payroll Africa" width="80" />
</p>

<h1 align="center">Payroll Africa</h1>

<p align="center">
  Statutory payroll deduction automation for <strong>54 African countries</strong>.<br/>
  Built on <a href="https://frappeframework.com">Frappe</a> + <a href="https://frappehr.com">HRMS</a>.
</p>

<p align="center">
  <a href="#supported-countries">Countries</a> &middot;
  <a href="#how-it-works">How It Works</a> &middot;
  <a href="#installation">Installation</a> &middot;
  <a href="#configuration">Configuration</a> &middot;
  <a href="#reports">Reports</a> &middot;
  <a href="#api">API</a> &middot;
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <a href="https://github.com/CoaleTech/payroll_africa/actions/workflows/ci.yml"><img src="https://github.com/CoaleTech/payroll_africa/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <img src="https://img.shields.io/badge/tests-347%20passing-brightgreen" alt="Tests" />
  <img src="https://img.shields.io/badge/countries-54-blue" alt="Countries" />
  <img src="https://img.shields.io/badge/license-GPL--3.0-blue" alt="License" />
  <img src="https://img.shields.io/badge/Frappe-v15%20%7C%20v16-0089FF" alt="Frappe" />
</p>

---

## Overview

Payroll Africa hooks into HRMS Salary Slip validation to automatically compute employee and employer statutory deductions — PAYE, social security, health insurance, housing levies, training funds, pension contributions — using each country's current tax bands and rates.

No manual calculation. No spreadsheets. Change a rate in settings, and the next payroll run picks it up.

### Key Features

- **Automatic deduction computation** on every Salary Slip save/submit via the HRMS `apply_regional_deductions` regional override
- **54 countries** — 54 calculators, 54 Settings DocTypes, 54 tax-band child tables
- **111 reports** — country-specific PAYE returns, social security remittances, and 5 cross-country reports
- **Country enable/disable** — toggle active countries in a single settings page; sidebar and component dropdowns update automatically (no restart)
- **Rate change tracking** — update statutory rates with effective dates; audit trail report included
- **Salary structure templates & income tax slabs** — pre-built for every country with statutory deductions (44 countries), with all statutory components wired up
- **Standalone deduction API** — calculate deductions for any country without creating a Salary Slip
- **Bulk recalculation** — recalculate all enabled countries' draft slips in one API call
- **Yearly rate-review reminder** — automated email to Payroll Managers each January
- **What's New dialog** — styled release notes surfaced after app updates
- **347 unit tests** — all passing, covering every country

---

## Supported Countries

### East Africa (11 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Kenya | KES | NSSF (Tier I & II), SHIF, Housing Levy (emp + empr), NITA |
| Uganda | UGX | NSSF (employee + employer), LST |
| Tanzania | TZS | NSSF, SDL, WCF — via HRMS PAYE |
| Rwanda | RWF | Pension, Maternity, CBHI, Occupational Hazards |
| Burundi | BIF | INSS, Work Injury, Health Insurance, Training Fund |
| Ethiopia | ETB | PIT (0–35%), Pension (Employee + Employer) |
| Djibouti | DJF | PIT, CNSS (Pension + Health) |
| Eritrea | ERN | PIT, NICE Social Insurance |
| Somalia | SOS | No mandatory statutory deductions |
| South Sudan | SSP | No standardised statutory framework |
| Sudan | SDG | PIT, NSIF Social Insurance |

### Southern Africa (11 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Malawi | MWK | PAYE, Pension |
| Zambia | ZMW | PAYE, NAPSA (capped), NHIMA |
| Mozambique | MZN | PAYE/IRPS, INSS |
| Angola | AOA | PAYE/IRT, INSS |
| Botswana | BWP | PAYE (0–26.5%) |
| South Africa | ZAR | PAYE (18–45%), UIF, SDL |
| Namibia | NAD | PAYE (0–37%), SSC, VET, ECF |
| Madagascar | MGA | IRSA (0–30%), CNaPS, OSTIE, FMFP |
| Zimbabwe | ZiG/USD | PAYE, NSSA (Employee + Employer), AIDS Levy |
| Lesotho | LSL | PAYE (annual tax credit applied) |
| Eswatini | SZL | PAYE, ENPF (Employee + Employer), SDL |

### West Africa (16 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Nigeria | NGN | Pension (PenCom), NHF, NHIS, NSITF, ITF — PAYE via HRMS |
| Ghana | GHS | SSNIT (Tier 1 Employee + Employer, Tier 2), PAYE |
| Ivory Coast | XOF | ITS (0–32%), CNPS Pension, Family Allowances, Housing, Training, Work Injury |
| Senegal | XOF | IPRES Pension (emp + empr), CSS Health, AMO Health, Income Tax |
| Mali | XOF | INSS Pension (emp + empr), AMO Health, PIT |
| Niger | XOF | CNSS Pension (emp + empr), AMO Health, PIT |
| Burkina Faso | XOF | CNSS Pension (emp + empr), AMO Health, PIT |
| Benin | XOF | CNSS Pension (emp + empr), AMO Health, PIT |
| Togo | XOF | CNSS (Employee + Employer), PIT/IRPP |
| Guinea | GNF | INSS Pension, Family Allowances, AMO Health, Work Injury, PIT |
| Sierra Leone | SLE | PAYE, NASSIT Pension (Employee + Employer) |
| Liberia | LRD | PAYE, NASSCorp Pension (Employee + Employer) |
| Gambia | GMD | PIT, SSHFC Provident Fund (Employee + Employer) |
| Guinea-Bissau | XOF | IRPS, INSS Social Insurance |
| Cabo Verde | CVE | IRPC, INPS (Employee + Employer), Work Injury |
| Mauritania | MRU | PIT, CNSS, CNAM Health |

### North Africa (5 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Egypt | EGP | PIT (0–27.5%), Social Insurance, Health Insurance, Martyrs Fund |
| Morocco | MAD | IR (0–37%), CNSS (Pension + AMO Health) |
| Tunisia | TND | IRPP (0–40%), CNSS, SSC |
| Algeria | DZD | PIT (0–35%), CNAS Social Security |
| Libya | LYD | PIT, SSF (Employee + Employer), Jehad Tax, Solidarity Fund |

### Central Africa (9 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| DRC | CDF | IPR/PAYE, INSS, INPP, ONEM, Family Benefits |
| Cameroon | XAF | IRPP, CNPS (Pension + Family), CFC Housing, FNE, CRTV, Taxe Communale, Work Injury |
| Gabon | XAF | IRGP, CNSS (Employee + Employer) |
| Congo | XAF | PIT, CNSS (Employee + Employer), CNAMGS Health |
| Central African Republic | XAF | PIT, CNSS (Employee + Employer) |
| Chad | XAF | PIT, CNPS (Pension + Family), Work Injury |
| Equatorial Guinea | XAF | PIT, CNSS (Employee + Employer) |
| Sao Tome and Principe | STN | PIT, INSS (Employee + Employer) |
| Comoros | KMF | PIT, CNSS (Employee + Employer) |

### Indian Ocean (3 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Mauritius | MUR | PAYE, NSF (Employee + Employer), CSG, HRDC, PRGF, Fair Share Contribution |
| Seychelles | SCR | PAYE, Social Security Employer Levy |
| Madagascar | MGA | *(see Southern Africa)* |

---

### Cross-Country Reports

| Report | Description |
|--------|-------------|
| Statutory Deductions Summary | All employee deductions by period — dynamic columns per component |
| Employer Contributions | Employer-only statutory costs per employee |
| Cost to Company | Total compensation including all employer contributions |
| Multi-Country Payroll Summary | Consolidated view across all enabled countries |
| Rate Change Audit Trail | History of statutory rate changes with effective dates |

---

## How It Works

```
Employee + Salary Structure
        |
        v
  Salary Slip (save/submit)
        |
        v
  HRMS regional override → payroll_africa.engine.salary_slip.apply_regional_deductions()
        |
        v
  registry.py → get_calculator(country)
        |
        v
  calculators/{country}.py → compute(salary_slip)
        |
        v
  Deduction / employer-contribution rows auto-populated with correct amounts
```

1. **Employee's country is resolved** from `Salary Structure Assignment.payroll_country`, falling back to `Employee.payroll_country`, then `Company.country`
2. **Country calculator is loaded** via the registry, which maps country names to calculator classes
3. **Calculator reads current rates** from the country's Settings DocType (e.g., `Kenya Payroll Settings`)
4. **Deductions / employer contributions are computed** using the country's tax bands, ceilings, and formulas
5. **Salary Slip rows are updated** — employee deductions go to `deductions`; employer-only contributions go to `employer_contributions` when the child table exists

If a country's Settings DocType has not been configured, all calculators fall back to hardcoded statutory defaults so payroll works immediately after installation.

---

## Installation

### Prerequisites

- Frappe v15 or v16
- ERPNext
- HRMS

### Install

Add **Payroll Africa** to your bench from the Frappe Cloud Marketplace. ERPNext and HRMS are provisioned automatically as dependencies.

On installation, the app provisions:
- Currency records for all required currencies
- `Employee.payroll_country` custom Link field
- Country-specific Salary Components for each deduction type
- Configurable Settings DocTypes with current statutory tax bands for all **54 countries**
- Income Tax Slabs and Salary Structure templates for every country with statutory deductions (**44 countries**)
- Workspace sidebar with country sections and reports, plus a Desktop icon under Frappe HR

> Somalia and South Sudan have no mandatory statutory deductions (documented no-ops), and Zimbabwe uses hardcoded PAYE bands — every other country exposes fully configurable rates and tax bands. Enable or disable any country in Payroll Africa Settings.

### Uninstall

When the app is removed, its `before_uninstall` step cleans up all salary structures, salary components, income tax slabs, and custom fields it created.

---

## Configuration

### Global Settings

Navigate to **Payroll Africa Settings** from the workspace sidebar or Home shortcut.

| Setting | Description |
|---------|-------------|
| Enable Payroll Africa | Master toggle — disables all computation when off |
| Country checkboxes | Enable/disable individual countries (grouped by region and tier) |

When a country is disabled:
- Its settings links and report links disappear from the workspace sidebar **immediately** (no restart — driven by `payroll_africa_sidebar.js` on page load and `extend_bootinfo`)
- The engine silently skips employees in that country
- Its salary components are hidden from Salary Structure component dropdowns

### Country Settings

Each country has its own Settings DocType in the sidebar. Every settings page includes:

- **Effective date** — track when rates last changed
- **Enabled toggle** — disable a single country without touching the global setting
- **Country-specific rate fields** — contribution percentages, ceilings, minimum wages
- **Tax band table** — update progressive tax brackets without code changes or redeployment

**Examples:**
- `Kenya Payroll Settings` — NSSF Tier I/II rates and caps, SHIF rate, Housing Levy rates, NITA amount, personal relief
- `South Africa Payroll Settings` — PAYE rebates, UIF rate and annual cap, SDL rate
- `Zimbabwe Payroll Settings` — PAYE bands (USD or ZiG), NSSA rate and annual ceiling, AIDS Levy rate, currency mode
- `Senegal Payroll Settings` — IPRES rates and ceiling, CSS Health rates, AMO Health toggle, income tax bands, family deductions
- `Mauritius Payroll Settings` — NSF rate and ceiling, CSG rate, HRDC rate, PRGF toggle, Fair Share Contribution toggle
- `Cameroon Payroll Settings` — CNPS rates, family allowances, work injury risk class, CFC housing, FNE rate, PIT abatement, CRTV bands, Taxe Communale bands

### Employee Setup

Set the **Payroll Country** field on each Employee record. The field is a Link to the standard Frappe Country DocType. If not set, the engine falls back to the Employee's Company country.

### Salary Structure

Use the pre-built template (e.g., "Kenya Payroll Template") or create your own. The calculator appends any missing statutory components automatically during Salary Slip validation — you do not need to add them manually.

---

## Reports

### By Country

| Region | Country | Reports |
|--------|---------|---------|
| East Africa | Kenya | P9A Tax Deduction Card, P10 Monthly Tax Return, NSSF Remittance, SHIF Remittance, Housing Levy Return |
| | Uganda | URA PAYE Return, NSSF Uganda Remittance, LST Return |
| | Tanzania | TRA Employment Taxes, NSSF Tanzania Remittance |
| | Rwanda | RRA Unified Declaration |
| | Burundi | OBR PAYE Return, INSS Burundi Remittance |
| | Ethiopia | Ethiopia PIT Remittance, Ethiopia Pension Remittance |
| | Djibouti | Djibouti IRPP Return, Djibouti CNSS Remittance |
| | Eritrea | Eritrea PIT Return, Eritrea NICE Remittance |
| | Sudan | Sudan PIT Return, Sudan NSIF Remittance |
| Southern Africa | Malawi | MRA P12 PAYE Return, MRA P9 Deduction Certificate |
| | Zambia | ZRA P11 PAYE Return, NAPSA Remittance, NHIMA Remittance |
| | Mozambique | AT IRPS Return, INSS Mozambique Remittance |
| | Angola | AGT IRT Return, INSS Angola Remittance |
| | Botswana | Botswana PAYE Return |
| | South Africa | South Africa PAYE Remittance, South Africa UIF Remittance |
| | Namibia | Namibia PAYE Return, Namibia SSC Remittance |
| | Madagascar | Madagascar IRSA Remittance, Madagascar CNAPPS Remittance |
| | Zimbabwe | Zimbabwe PAYE Return, Zimbabwe NSSA Remittance |
| | Lesotho | Lesotho PAYE Return |
| | Eswatini | Eswatini PAYE Return, Eswatini ENPF Remittance |
| | Liberia | Liberia PAYE Return, Liberia NASSCorp Remittance |
| | Sierra Leone | Sierra Leone PAYE Return, Sierra Leone NASSIT Remittance |
| West Africa | Nigeria | Nigeria PAYE Schedule, PenCom Remittance, NHF Remittance, NHIS Schedule |
| | Ghana | Ghana PAYE Schedule, Ghana SSNIT Remittance |
| | Ivory Coast | Ivory Coast ITS Remittance, Ivory Coast CNPS Remittance |
| | Senegal | Senegal IR Return, Senegal IPRES Remittance |
| | Mali | Mali PIT Return, Mali INSS Remittance |
| | Niger | Niger PIT Return, Niger CNSS Remittance |
| | Burkina Faso | Burkina Faso PIT Return, Burkina Faso CNSS Remittance |
| | Benin | Benin PIT Return, Benin CNSS Remittance |
| | Togo | Togo PIT Return, Togo CNSS Remittance |
| | Guinea | Guinea PIT Return, Guinea INSS Remittance |
| | Gambia | Gambia PIT Return, Gambia SSHFC Remittance |
| | Guinea-Bissau | Guinea-Bissau IRPS Return, Guinea-Bissau INSS Remittance |
| | Cabo Verde | Cabo Verde IRPC Return, Cabo Verde INPS Remittance |
| | Mauritania | Mauritania PIT Return, Mauritania CNSS Remittance |
| North Africa | Egypt | Egypt Income Tax Return, Egypt Social Insurance Remittance |
| | Morocco | Morocco IR Remittance, Morocco CNSS Remittance |
| | Tunisia | Tunisia IRPP Remittance, Tunisia CNSS Remittance |
| | Algeria | Algeria PIT Return, Algeria CNAS Remittance |
| | Libya | Libya PIT Return, Libya SSF Remittance |
| Central Africa | DRC | DRC Unified Declaration |
| | Cameroon | Cameroon IRPP Return, Cameroon CNPS Remittance |
| | Gabon | Gabon IRGP Return, Gabon CNSS Remittance |
| | Congo | Congo PIT Return, Congo CNSS Remittance |
| | CAR | CAR PIT Return, CAR CNSS Remittance |
| | Chad | Chad PIT Return, Chad CNPS Remittance |
| | Equatorial Guinea | Equatorial Guinea PIT Return, Equatorial Guinea CNSS Remittance |
| | Sao Tome | Sao Tome PIT Return, Sao Tome INSS Remittance |
| | Comoros | Comoros PIT Return, Comoros CNSS Remittance |
| Indian Ocean | Mauritius | Mauritius PAYE Return, Mauritius NSF Remittance |
| | Seychelles | Seychelles PAYE Return |

---

## API

All functions are `@frappe.whitelist()` decorated and accessible via REST.

### `calculate_deductions`

Compute deductions for any country without creating a Salary Slip — useful for simulations and what-if analysis.

```python
from payroll_africa.api import calculate_deductions

result = calculate_deductions("Kenya", gross_pay=100000)
# {
#   "country": "Kenya",
#   "gross_pay": 100000.0,
#   "basic_pay": 100000.0,
#   "deductions": [
#     {"component": "NSSF Employee", "amount": 2160.0, "is_employer_only": False},
#     {"component": "NSSF Employer", "amount": 2160.0, "is_employer_only": True},
#     ...
#   ],
#   "employee_total": 6035.0,
#   "employer_total": 3210.0,
#   "net_pay": 93965.0,
#   "cost_to_company": 103210.0
# }
```

### `get_supported_countries`

Return sorted list of all 54 supported country names.

### `recalculate_salary_slips`

Recalculate all draft Salary Slips for a single country in a date range:

```python
from payroll_africa.api import recalculate_salary_slips

result = recalculate_salary_slips("Kenya", "2025-01-01", "2025-12-31", company="My Co")
# {"updated": 42, "errors": [], "message": "42 salary slip(s) recalculated"}
```

### `recalculate_all_countries`

Recalculate draft slips for every enabled country in one call:

```python
from payroll_africa.api import recalculate_all_countries

result = recalculate_all_countries("2025-01-01", "2025-12-31")
# {
#   "updated": 142,
#   "errors": {},
#   "by_country": {"Kenya": {...}, "Uganda": {...}, ...},
#   "message": "142 salary slip(s) recalculated across 5 countries"
# }
```

### REST

```bash
curl -X POST /api/method/payroll_africa.api.calculate_deductions \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d '{"country": "Kenya", "gross_pay": 100000}'

curl -X POST /api/method/payroll_africa.api.recalculate_all_countries \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d '{"from_date": "2025-01-01", "to_date": "2025-12-31"}'
```

---

## Architecture

```
payroll_africa/
├── calculators/          # 54 country calculator classes + base.py
│   ├── base.py           #   BaseCalculator (abstract)
│   ├── kenya.py          #   KenyaCalculator — compute() → {component: {amount, is_employer_only}}
│   └── ...               #   one file per country
├── engine/
│   ├── hooks.py          # Employee country resolution helper
│   ├── salary_slip.py    # HRMS apply_regional_deductions override
│   ├── utils.py          # Effective Salary Structure Assignment helpers
│   └── registry.py       # COUNTRY_MAP, SETTINGS_MAP — country → calculator + DocType lookup
├── boot.py               # extend_bootinfo: injects enabled countries into frappe.boot
├── api.py                # 5 whitelisted API endpoints
├── tasks.py              # Yearly scheduler: notify_rate_review
├── setup.py              # after_install / before_uninstall lifecycle
├── hooks.py              # regional_overrides, scheduler_events, fixtures, boot_session, app_include_js/css
├── payroll_africa/
│   ├── doctype/
│   │   ├── payroll_africa_settings/    # Single DocType — global toggle + 54 country checkboxes
│   │   ├── {country}_payroll_settings/ # 54 Single DocTypes — configurable rates per country
│   │   └── {country}_{tax}_band/       # 56 child table DocTypes — progressive tax brackets
│   ├── report/                         # 111 reports (5 cross-country + 106 country-specific)
│   └── workspace/                      # Workspace with shortcuts + links
├── workspace_sidebar/    # 139-item sidebar — dynamically filtered by enabled countries
├── change_log/           # Release notes (v0.0.3)
├── fixtures/             # Custom fields + 21 Income Tax Slabs
├── public/
│   ├── js/
│   │   ├── payroll_africa_change_log.js       # What's New dialog
│   │   ├── payroll_africa_salary_structure.js # Hides disabled countries' components
│   │   └── payroll_africa_sidebar.js          # Hides disabled countries' sidebar links
│   └── css/
│       ├── payroll_africa.css
│       └── payroll_africa_change_log.css
├── demo/                 # Demo data setup/teardown scripts
└── tests/                # 347 unit tests — all 54 countries + API + engine + reports
```

### Calculator Pattern

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

The registry maps country names to calculator classes and loads settings:

```python
# engine/registry.py
COUNTRY_MAP = {
    "Kenya":  "payroll_africa.calculators.kenya.KenyaCalculator",
    "Senegal": "payroll_africa.calculators.senegal.SenegalCalculator",
    # ... 54 entries
}

def get_calculator(country):
    settings = get_country_settings(country) or frappe._dict()
    return CalculatorClass(settings)
```

Calculators fall back to hardcoded statutory defaults when the settings DocType is empty, so payroll runs correctly out of the box.

---

## Adding a New Country

1. **Create the calculator** — `calculators/{snake}.py` extending `BaseCalculator`, implementing `compute()` returning `{component: {amount, is_employer_only}}`
2. **Create Settings DocType** — `{country}_payroll_settings` (Single DocType) with rate fields and a tax band child table
3. **Create Band DocType** — `{country}_paye_band` or `{country}_pit_band` (child table: `from_amount`, `to_amount`, `rate`)
4. **Register** — add entries to `COUNTRY_MAP` and `SETTINGS_MAP` in `engine/registry.py`
5. **Boot** — add `"Country Name": "enable_{snake}"` to `COUNTRY_FIELD_MAP` in `boot.py`
6. **Settings toggle** — add `enable_{snake}` Check field to `payroll_africa_settings.json`
7. **Sidebar** — add settings link to `workspace_sidebar/payroll_africa.json`
8. **Reports** — create tax return and social security remittance reports in `payroll_africa/report/`
9. **Tests** — add a test class with zero gross, rate spot-check, employer flag, ceiling, and PIT threshold tests
10. **Migrate** — run a site database migration to install the new DocTypes

---

## Contributing

```bash
cd apps/payroll_africa
pre-commit install   # ruff, eslint, prettier, pyupgrade
```

### Running Tests

```bash
bench --site your-site run-tests --app payroll_africa
```

**347 tests, all passing.** Coverage spans all 54 countries.

#### Test files

| File | Coverage | Tests |
|------|----------|-------|
| `test_kenya_calculator.py` | Kenya — NSSF tiers, Housing Levy, NITA | 12 |
| `test_nigeria_calculator.py` | Nigeria — PenCom, NHF, NHIS | 9 |
| `test_burundi_calculator.py` | Burundi — INSS, work injury, health | 9 |
| `test_{country}_calculator.py` (×18) | One per Tier 1 country | 4–8 each |
| `test_tier2_calculators.py` | Algeria, Senegal, Cameroon, Mauritius, Zimbabwe, Mali, Niger, Burkina Faso, Benin | 48 |
| `test_tier3_calculators.py` | Gabon, Congo, Guinea, Chad, Liberia, Sierra Leone, Togo, Eswatini, Seychelles | 48 |
| `test_tier4_calculators.py` | Cabo Verde, CAR, Comoros, Djibouti, Equatorial Guinea, Eritrea, Gambia, Guinea-Bissau, Lesotho, Libya, Mauritania, Sao Tome, Somalia, South Sudan, Sudan | 78 |
| `test_reports.py` | Report column structure and filter conditions | 22 |
| `test_api.py` | API endpoints — deductions, countries, recalculate | 11 |
| `test_engine.py` | Salary Slip hook — dispatch, guard, skip logic | 10 |

#### What each calculator test validates

Every country (except Somalia/South Sudan stubs) tests:

- **Zero gross** — zero salary returns zero amounts and no PIT/PAYE
- **Rate spot-check** — deduction amounts verified against published statutory rates
- **Employer-only flag** — `is_employer_only: True` for employer components, `False` for employee
- **Ceiling/cap** — contributions correctly capped when gross exceeds the statutory ceiling
- **PIT threshold** — no income tax below the tax-free threshold; tax present and non-zero above it

---

## License

GPL-3.0
