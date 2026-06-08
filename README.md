<p align="center">
  <img src="payroll_africa/public/icons/africa.svg" alt="Payroll Africa" width="80" />
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
  <a href="#api">API</a>
</p>

---

## Overview

Payroll Africa hooks into HRMS Salary Slip validation to automatically compute employee and employer statutory deductions — PAYE, social security, health insurance, housing levies, training funds, pension contributions — using each country's current tax bands and rates.

No manual calculation. No spreadsheets. Change a rate in settings, and the next payroll run picks it up.

### Key Features

- **Automatic deduction computation** on Salary Slip save/submit
- **54 countries** with country-specific calculators, configurable tax bands, and statutory rates
- **110+ reports** covering PAYE returns, social security remittances, and compliance filings
- **Country enable/disable** — toggle which countries are active in your deployment
- **Dynamic workspace** — sidebar and salary component dropdowns filter to show only enabled countries
- **Rate change tracking** — update statutory rates with effective dates; audit trail included
- **Template salary structures** — pre-built per country with all statutory components wired up
- **API for standalone calculations** — compute deductions without creating a Salary Slip
- **Bulk recalculation** — recalculate all enabled countries' draft slips in one API call
- **Yearly rate-review reminder** — automated email to Payroll Managers at year-start
- **Print format** — "Salary Slip Africa Standard" with country-aware layout
- **What's New dialog** — styled release notes shown after app updates

---

## Supported Countries

### East Africa (15 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Kenya | KES | PAYE, NSSF (Tier I & II), SHIF, Housing Levy, NITA |
| Uganda | UGX | PAYE, NSSF (5%/10%/15% tiers), LST |
| Tanzania | TZS | PAYE, NSSF, SDL, WCF |
| Rwanda | RWF | PAYE, Pension, Maternity, CBHI, Occupational Hazards |
| Burundi | BIF | PAYE, INSS, Work Injury, Health Insurance, Training Fund |
| Ethiopia | ETB | PIT (0–35%), Pension (Employee + Employer) |
| Djibouti | DJF | PIT, CNSS (Pension + Health) |
| Eritrea | ERN | PIT, NICE Social Insurance |
| Somalia | SOS | No mandatory statutory deductions |
| South Sudan | SSP | No standardized statutory framework |
| Sudan | SDG | PIT, NSIF Social Insurance |

### Southern Africa (9 countries)

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
| Zimbabwe | ZiG/USD | PAYE, NSSA, AIDS Levy |
| Lesotho | LSL | PAYE (annual tax credit) |
| Eswatini | SZL | PAYE, ENPF, SDL |

### West Africa (14 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Nigeria | NGN | PAYE, Pension (PenCom), NHF, NHIS, NSITF, ITF |
| Ghana | GHS | PAYE (0–35%), SSNIT (Tier 1 & 2) |
| Ivory Coast | XOF | ITS (0–32%), CNPS (Pension + Family) |
| Senegal | XOF | IR (0–40%), IPRES, CSS, AMO Health |
| Mali | XOF | PIT, INSS Pension, AMO Health |
| Niger | XOF | PIT, CNSS Pension, AMO Health |
| Burkina Faso | XOF | PIT, CNSS Pension, AMO Health |
| Benin | XOF | PIT, CNSS Pension, AMO/CRAMI Health |
| Togo | XOF | PIT/IRPP, CNSS Pension |
| Guinea | GNF | PIT, INSS (Pension + Family), AMO, Work Injury |
| Sierra Leone | SLE | PAYE, NASSIT Pension |
| Liberia | LRD | PAYE, NASSCorp Pension |
| Gambia | GMD | PIT, SSHFC Provident Fund |
| Guinea-Bissau | XOF | IRPS, INSS Social Insurance |
| Cabo Verde | CVE | IRPC, INPS, Work Injury |
| Mauritania | MRU | PIT, CNSS, CNAM Health |

### North Africa (5 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Egypt | EGP | PIT (0–27.5%), Social Insurance, Health Insurance, Martyrs Fund |
| Morocco | MAD | IR (0–37%), CNSS (Pension + AMO) |
| Tunisia | TND | IRPP (0–40%), CNSS, SSC |
| Algeria | DZD | PIT (0–35%), CNAS Social Security |
| Libya | LYD | PIT, SSF, Jehad Tax, Solidarity Fund |

### Central Africa (9 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| DRC | CDF | IPR/PAYE, INSS, INPP, ONEM, Family Benefits |
| Cameroon | XAF | IRPP, CNPS (Pension + Family), CFC Housing, FNE, Work Injury |
| Gabon | XAF | IRGP, CNSS (Pension + Health) |
| Congo | XAF | PIT, CNSS (Employee + Employer), CNAMGS Health |
| Central African Republic | XAF | PIT, CNSS Social Insurance |
| Chad | XAF | PIT, CNPS (Pension + Family), Work Injury |
| Equatorial Guinea | XAF | PIT, CNSS Social Insurance |
| Sao Tome and Principe | STN | PIT, INSS Social Insurance |
| Comoros | KMF | PIT, CNSS Social Insurance |

### Indian Ocean (3 countries)

| Country | Currency | Key Statutory Deductions |
|---------|----------|--------------------------|
| Mauritius | MUR | PAYE, NSF, CSG, HRDC, PRGF, Fair Share Contribution |
| Seychelles | SCR | PAYE, Social Security Employer Levy |
| Madagascar | MGA | *(see Southern Africa above)* |

---

### Cross-Country Reports

| Report | Description |
|--------|-------------|
| Statutory Deductions Summary | All deductions by employee and period |
| Employer Contributions | Employer-only statutory costs |
| Cost to Company | Total compensation including employer contributions |
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
  engine/hooks.py → on_salary_slip_validate()
        |
        v
  registry.py → get_calculator(country)
        |
        v
  calculators/{country}.py → compute(doc)
        |
        v
  Deduction rows auto-populated with correct amounts
```

1. **Employee's country is resolved** from `Employee.payroll_country` (custom field), falling back to `Company.country`
2. **Country calculator is loaded** via the registry, which maps countries to their calculator classes
3. **Calculator reads current rates** from the country's Settings DocType (e.g., "Kenya Payroll Settings")
4. **Deductions are computed** using the country's tax bands, caps, and formulas
5. **Salary Slip rows are updated** — existing deduction rows get overwritten, missing components get appended

If a country's Settings DocType has not been configured, all calculators fall back to hardcoded statutory defaults so payroll can run immediately after installation.

---

## Installation

### Prerequisites

- Frappe v15 or v16
- ERPNext
- HRMS

### Install

```bash
cd /path/to/your/bench
bench get-app <repo-url> --branch main
bench install-app payroll_africa
bench --site your-site migrate
```

The `after_install` hook automatically creates:
- Country-specific Payroll Settings with current statutory rates
- Salary Components for each enabled country's deductions
- Income Tax Slabs with PAYE/PIT bands
- Template Salary Structures (e.g., "Kenya Payroll Template")
- Workspace sidebar with country sections and reports
- Desktop icon under Frappe HR

### Uninstall

```bash
bench uninstall-app payroll_africa
```

The `before_uninstall` hook removes all salary structures, salary components, income tax slabs, custom fields, and desktop icons created by the app.

---

## Configuration

### Global Settings

Navigate to **Payroll Africa Settings** from the workspace.

| Setting | Description |
|---------|-------------|
| Enable Payroll Africa | Master toggle — disables all computation when off |
| Country checkboxes | Enable/disable individual countries (grouped by tier/region) |

Countries are grouped into three tiers in the settings page:
- **Tier 1** (original 21 countries) — fully production-ready with complete reports
- **Tier 2** (Algeria, Senegal, Cameroon, Mauritius, Zimbabwe, Mali, Niger, Burkina Faso, Benin, Gabon, Congo, Guinea, Togo, Seychelles)
- **Tier 4** (remaining 19 countries) — calculators functional with statutory defaults

When a country is disabled:
- Its settings and report links are hidden from the workspace sidebar automatically (no restart required)
- The payroll calculator silently skips employees in that country
- Its salary components are hidden from Salary Structure dropdowns

### Country Settings

Each country has its own Settings DocType accessible from the workspace sidebar. Every settings page includes:
- Effective date
- Enabled toggle
- Country-specific rate fields (contribution percentages, ceilings, etc.)
- Tax band table (configure progressive brackets without code changes)

**East Africa examples:**
- **Kenya Payroll Settings** — PAYE relief, NSSF tiers, SHIF rate, Housing Levy rate, NITA rate
- **Ethiopia Payroll Settings** — PIT bands (6 progressive brackets), Pension rates

**Southern Africa examples:**
- **South Africa Payroll Settings** — PAYE rebates (primary/secondary/tertiary), UIF rate and annual cap, SDL rate
- **Zimbabwe Payroll Settings** — PAYE bands (USD or ZiG), NSSA rate and ceiling, AIDS Levy rate, currency mode

**West Africa examples:**
- **Senegal Payroll Settings** — IPRES rates and ceiling, CSS Health rates, AMO Health toggle, IR bands, family deductions
- **Mauritius Payroll Settings** — NSF rate and ceiling, CSG rate, HRDC rate, PRGF toggle, Fair Share Contribution toggle

Each settings page includes a Tax Bands table where you can update tax brackets when legislation changes — no code deployment required.

### Employee Setup

Set the **Payroll Country** field on each Employee record. If not set, the system falls back to the Employee's Company country.

### Salary Structure

Use the pre-built template (e.g., "Kenya Payroll Template") or create your own. The calculator will append missing statutory components automatically during Salary Slip validation.

---

## Reports

### Reports by Country

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
| | Liberia | *(see Southern Africa)* |
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

### Calculate Deductions (standalone)

Compute deductions without creating a Salary Slip — useful for salary simulations and what-if analysis.

```python
from payroll_africa.api import calculate_deductions

result = calculate_deductions("Kenya", gross_pay=100000)
# Returns:
# {
#     "deductions": [...],
#     "employee_total": 15234.00,
#     "employer_total": 8500.00,
#     "net_pay": 84766.00,
#     "cost_to_company": 108500.00
# }
```

### Recalculate Draft Salary Slips (single country)

After updating statutory rates, recalculate all draft Salary Slips in a date range:

```python
from payroll_africa.api import recalculate_salary_slips

result = recalculate_salary_slips(
    "Kenya",
    "2025-01-01",
    "2025-12-31",
    company="My Company"  # optional filter
)
```

### Recalculate All Enabled Countries

Recalculate draft slips for every country enabled in Payroll Africa Settings in one call:

```python
from payroll_africa.api import recalculate_all_countries

result = recalculate_all_countries(
    "2025-01-01",
    "2025-12-31",
    company="My Company"  # optional filter
)
# Returns:
# {
#     "updated": 142,
#     "errors": [],
#     "by_country": {"Kenya": {...}, "Uganda": {...}, ...},
#     "message": "142 salary slip(s) recalculated across 5 countries"
# }
```

### REST API

All functions are whitelisted and accessible via REST:

```bash
# Calculate deductions
curl -X POST /api/method/payroll_africa.api.calculate_deductions \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d '{"country": "Kenya", "gross_pay": 100000}'

# Recalculate all countries at once
curl -X POST /api/method/payroll_africa.api.recalculate_all_countries \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d '{"from_date": "2025-01-01", "to_date": "2025-12-31"}'
```

---

## Architecture

```
payroll_africa/
├── calculators/          # Country-specific calculator classes (54 countries)
│   ├── base.py           #   BaseCalculator (abstract)
│   ├── kenya.py          #   KenyaCalculator
│   ├── senegal.py        #   SenegalCalculator
│   └── ...               #   (54 total)
├── engine/
│   ├── hooks.py          # Salary Slip validate hook
│   └── registry.py       # Country → Calculator mapping + settings DocType lookup
├── boot.py               # extend_bootinfo (enabled countries → frappe.boot)
├── api.py                # Whitelisted API endpoints
├── tasks.py              # Scheduler tasks (yearly rate-review email)
├── setup.py              # after_install / after_migrate / before_uninstall
├── hooks.py              # App hooks, scheduler_events, fixtures config
├── payroll_africa/
│   ├── doctype/
│   │   ├── payroll_africa_settings/   # Global settings (Single DocType, 54 country toggles)
│   │   ├── kenya_payroll_settings/    # Country settings (×54)
│   │   └── kenya_paye_band/           # PAYE/tax band child table (×54)
│   ├── report/                        # 110+ reports (5 cross-country + country-specific)
│   ├── print_format/                  # Salary Slip Africa Standard
│   └── workspace/                     # Workspace definition
├── workspace_sidebar/    # Sidebar template (filtered by enabled countries at runtime)
├── change_log/           # Release notes (shown in What's New dialog)
├── fixtures/             # Custom fields + Income Tax Slabs
├── public/
│   ├── css/              # Sidebar icon + change log styling
│   ├── js/
│   │   ├── payroll_africa_change_log.js      # What's New dialog renderer
│   │   ├── payroll_africa_salary_structure.js # Component dropdown filter
│   │   └── payroll_africa_sidebar.js         # Dynamic sidebar hide/show (54-country aware)
│   └── icons/            # Africa SVG icon
├── demo/                 # Demo data setup/teardown
└── tests/                # Calculator unit tests (54 countries)
```

### Calculator Pattern

Each country implements a calculator class extending `BaseCalculator`:

```python
class KenyaCalculator(BaseCalculator):
    def compute(self, doc):
        # Read current rates from Kenya Payroll Settings
        # Apply PAYE bands, NSSF tiers, SHIF, Housing Levy, NITA
        # Return dict of component_name → {amount, is_employer_only}
        ...
```

All calculators use hardcoded statutory defaults when the settings DocType is not yet configured, so payroll works out of the box.

The registry (`engine/registry.py`) maps country names to calculator classes:

```python
COUNTRY_MAP = {
    "Kenya": "payroll_africa.calculators.kenya.KenyaCalculator",
    "Senegal": "payroll_africa.calculators.senegal.SenegalCalculator",
    # ... 54 countries total
}
```

---

## Adding a New Country

1. **Create the calculator** — `calculators/newcountry.py` extending `BaseCalculator`, implementing `compute(salary_slip)` returning `{component_name: {amount, is_employer_only}}`
2. **Create the Settings DocType** — "New Country Payroll Settings" (Single DocType) with rate fields and tax bands table
3. **Create the Tax Band DocType** — "New Country PAYE Band" (child table with `from_amount`, `to_amount`, `rate`)
4. **Register in registry.py** — add entries to `COUNTRY_MAP` and `SETTINGS_MAP`
5. **Register in boot.py** — add entry to `COUNTRY_FIELD_MAP` with field name `enable_newcountry`
6. **Add checkbox** — add `enable_newcountry` Check field to `payroll_africa_settings.json`
7. **Add sidebar items** — add settings link and reports section to `workspace_sidebar/payroll_africa.json`
8. **Create reports** — country-specific tax return and social security remittance reports
9. **Run `bench migrate`**

---

## Contributing

This app uses `pre-commit` for code formatting and linting:

```bash
cd apps/payroll_africa
pre-commit install
```

Tools configured:
- **ruff** — Python linting and formatting
- **eslint** — JavaScript linting
- **prettier** — Code formatting
- **pyupgrade** — Python syntax modernization

### Running Tests

```bash
bench --site your-site run-tests --app payroll_africa
```

Calculator unit tests live in `tests/` — one file per country tier (test_botswana_calculator.py, test_tier2_calculators.py, test_tier3_calculators.py, test_tier4_calculators.py, etc.).

---

## License

GPL-3.0
