<p align="center">
  <img src="payroll_africa/public/icons/africa.svg" alt="Payroll Africa" width="80" />
</p>

<h1 align="center">Payroll Africa</h1>

<p align="center">
  Statutory payroll deduction automation for 20 African countries.<br/>
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

Payroll Africa hooks into HRMS Salary Slip validation to automatically compute employee and employer statutory deductions — PAYE, social security, health insurance, housing levies, training funds — using each country's current tax bands and rates.

No manual calculation. No spreadsheets. Change a rate in settings, and the next payroll run picks it up.

### Key Features

- **Automatic deduction computation** on Salary Slip save/submit
- **20 countries** with country-specific calculators, tax bands, and statutory rates
- **51 reports** covering PAYE returns, social security remittances, and compliance filings
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

**East Africa**

| Country | Currency | Statutory Deductions | Reports |
|---------|----------|---------------------|---------|
| Kenya | KES | PAYE, NSSF (Tier I & II), SHIF, Housing Levy, NITA | P9A, P10, NSSF, SHIF, Housing Levy |
| Uganda | UGX | PAYE, NSSF (5%/10%/15% tiers), LST | URA PAYE Return, NSSF, LST |
| Tanzania | TZS | PAYE, NSSF, SDL, WCF | TRA Employment Taxes, NSSF |
| Rwanda | RWF | PAYE, Pension, Maternity, CBHI, Occupational Hazards | RRA Unified Declaration |
| Burundi | BIF | PAYE, INSS, Work Injury, Health Insurance, Training Fund | OBR PAYE Return, INSS |
| Ethiopia | ETB | PIT (5–35%), Pension (Employee + Employer) | Ethiopia PIT Return, Pension Remittance |

**Southern Africa**

| Country | Currency | Statutory Deductions | Reports |
|---------|----------|---------------------|---------|
| Malawi | MWK | PAYE, Pension | MRA P12, MRA P9 |
| Zambia | ZMW | PAYE, NAPSA (capped), NHIMA | ZRA P11, NAPSA, NHIMA |
| Mozambique | MZN | PAYE/IRPS, INSS | AT IRPS Return, INSS |
| Angola | AOA | PAYE/IRT, INSS | AGT IRT Return, INSS |
| Botswana | BWP | PAYE (0–26.5%) | Botswana PAYE Return |
| South Africa | ZAR | PAYE (18–45%), UIF | PAYE Remittance, UIF Remittance |
| Namibia | NAD | PAYE (0–37%), SSC | Namibia PAYE Return, SSC Remittance |
| Madagascar | MGA | IRSA (0–30%), CNAPPS | IRSA Remittance, CNAPPS Remittance |

**West & Central Africa**

| Country | Currency | Statutory Deductions | Reports |
|---------|----------|---------------------|---------|
| Nigeria | NGN | PAYE, Pension (PenCom), NHF, NHIS, NSITF, ITF | PAYE Schedule, PenCom, NHF, NHIS |
| Ghana | GHS | PAYE (0–35%), SSNIT | Ghana PAYE Schedule, SSNIT Remittance |
| Ivory Coast | XOF | ITS (0–32%), CNPS | ITS Remittance, CNPS Remittance |
| DRC | CDF | PAYE/IPR, INSS Pension, Occupational Risks, Family Benefits, INPP, ONEM | DRC Unified Declaration |

**North Africa**

| Country | Currency | Statutory Deductions | Reports |
|---------|----------|---------------------|---------|
| Egypt | EGP | Income Tax (0–27.5%), Social Insurance | Income Tax Return, Social Insurance Remittance |
| Morocco | MAD | IR (0–37%), CNSS | IR Remittance, CNSS Remittance |
| Tunisia | TND | IRPP (0–40%), CNSS | IRPP Remittance, CNSS Remittance |

**Cross-country reports** (work across all enabled countries):

| Report | Description |
|--------|-------------|
| Statutory Deductions Summary | All deductions by employee and period |
| Employer Contributions | Employer-only statutory costs |
| Cost to Company | Total compensation including employer contributions |
| Multi-Country Payroll Summary | Consolidated view across countries |
| Rate Change Audit Trail | History of statutory rate changes |

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
- Currency records for all 20 countries (KES, UGX, TZS, RWF, BIF, ETB, ZMW, MWK, MZN, AOA, BWP, ZAR, NAD, MGA, NGN, GHS, XOF, CDF, EGP, MAD, TND)
- Country-specific Payroll Settings with current statutory rates
- Salary Components for each country's deductions
- Income Tax Slabs with PAYE bands for all 20 countries
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
| Country checkboxes | Enable/disable individual countries |

When a country is disabled:
- Its settings and report links are hidden from the workspace sidebar automatically (no restart required — driven by `payroll_africa_sidebar.js` on page load)
- The payroll calculator silently skips employees in that country
- Its salary components are hidden from Salary Structure dropdowns

### Country Settings

Each country has its own Settings DocType accessible from the workspace sidebar:

**East Africa**
- **Kenya Payroll Settings** — PAYE relief, NSSF tiers, SHIF rate, Housing Levy rate, NITA rate
- **Uganda Payroll Settings** — NSSF tier rates, LST bands
- **Tanzania Payroll Settings** — NSSF rate, SDL rate, WCF rate
- **Rwanda Payroll Settings** — Pension rates, Maternity rates, CBHI rate
- **Burundi Payroll Settings** — INSS rates, Health Insurance rates, Training Fund rates
- **Ethiopia Payroll Settings** — PIT bands, Pension rates (Employee + Employer)

**Southern Africa**
- **Malawi Payroll Settings** — Pension rate
- **Zambia Payroll Settings** — NAPSA rate and cap, NHIMA rate
- **Mozambique Payroll Settings** — INSS rates
- **Angola Payroll Settings** — INSS rates
- **Botswana Payroll Settings** — PAYE bands
- **South Africa Payroll Settings** — PAYE rebates, UIF rate and annual cap
- **Namibia Payroll Settings** — PAYE bands, SSC rates
- **Madagascar Payroll Settings** — IRSA bands, CNAPPS rates

**West & Central Africa**
- **Nigeria Payroll Settings** — Pension rate (PenCom), NHF rate, NHIS rate, NSITF rate, ITF rate
- **Ghana Payroll Settings** — PAYE bands, SSNIT rate
- **Ivory Coast Payroll Settings** — ITS bands, CNPS rates
- **DRC Payroll Settings** — INSS rates, INPP rate, ONEM rate

**North Africa**
- **Egypt Payroll Settings** — Income tax bands, Social Insurance rates
- **Morocco Payroll Settings** — IR bands, CNSS rates
- **Tunisia Payroll Settings** — IRPP bands, CNSS rates

Each settings page includes a PAYE Bands table where you can update tax brackets when legislation changes.

### Employee Setup

Set the **Payroll Country** field on each Employee record. If not set, the system falls back to the Employee's Company country.

### Salary Structure

Use the pre-built template (e.g., "Kenya Payroll Template") or create your own. The calculator will append missing statutory components automatically during Salary Slip validation.

---

## Reports

### Kenya (5 reports)
| Report | Purpose |
|--------|---------|
| P9A Tax Deduction Card | Annual employee tax certificate |
| P10 Monthly Tax Return | Monthly PAYE filing to KRA |
| NSSF Remittance | NSSF contribution schedule |
| SHIF Remittance | Social Health Insurance Fund report |
| Housing Levy Return | Affordable Housing Levy report |

### Uganda (3 reports)
| Report | Purpose |
|--------|---------|
| URA PAYE Return | Monthly PAYE return for URA |
| NSSF Uganda Remittance | NSSF contribution schedule |
| LST Return | Local Service Tax report |

### Tanzania (2 reports)
| Report | Purpose |
|--------|---------|
| TRA Employment Taxes | PAYE + SDL + WCF report for TRA |
| NSSF Tanzania Remittance | NSSF contribution schedule |

### Rwanda (1 report)
| Report | Purpose |
|--------|---------|
| RRA Unified Declaration | Combined PAYE + social security filing |

### Burundi (2 reports)
| Report | Purpose |
|--------|---------|
| OBR PAYE Return | Monthly PAYE return for OBR |
| INSS Burundi Remittance | INSS contribution schedule |

### Zambia (3 reports)
| Report | Purpose |
|--------|---------|
| ZRA P11 PAYE Return | Monthly PAYE return for ZRA |
| NAPSA Remittance | Pension contribution schedule |
| NHIMA Remittance | Health insurance contribution schedule |

### Malawi (2 reports)
| Report | Purpose |
|--------|---------|
| MRA P12 PAYE Return | Monthly PAYE return for MRA |
| MRA P9 Deduction Certificate | Annual employee tax certificate |

### DRC (1 report)
| Report | Purpose |
|--------|---------|
| DRC Unified Declaration | Combined IPR + INSS + INPP + ONEM filing |

### Nigeria (4 reports)
| Report | Purpose |
|--------|---------|
| Nigeria PAYE Schedule | Monthly PAYE computation schedule |
| PenCom Remittance | Pension contribution schedule |
| NHF Remittance | National Housing Fund report |
| NHIS Schedule | Health insurance contribution schedule |

### Mozambique (2 reports)
| Report | Purpose |
|--------|---------|
| AT IRPS Return | Monthly PAYE/IRPS return |
| INSS Mozambique Remittance | INSS contribution schedule |

### Angola (2 reports)
| Report | Purpose |
|--------|---------|
| AGT IRT Return | Monthly PAYE/IRT return |
| INSS Angola Remittance | INSS contribution schedule |

### Botswana (1 report)
| Report | Purpose |
|--------|---------|
| Botswana PAYE Return | Monthly PAYE return for BURS |

### South Africa (2 reports)
| Report | Purpose |
|--------|---------|
| South Africa PAYE Remittance | Monthly PAYE remittance to SARS |
| South Africa UIF Remittance | UIF contribution schedule |

### Namibia (2 reports)
| Report | Purpose |
|--------|---------|
| Namibia PAYE Return | Monthly PAYE return for NamRA |
| Namibia SSC Remittance | Social Security Commission schedule |

### Madagascar (2 reports)
| Report | Purpose |
|--------|---------|
| Madagascar IRSA Remittance | Monthly IRSA salary tax return |
| Madagascar CNAPPS Remittance | CNAPPS pension contribution schedule |

### Ethiopia (2 reports)
| Report | Purpose |
|--------|---------|
| Ethiopia PIT Remittance | Monthly Personal Income Tax return |
| Ethiopia Pension Remittance | Pension contribution schedule |

### Ghana (2 reports)
| Report | Purpose |
|--------|---------|
| Ghana PAYE Schedule | Monthly PAYE computation schedule |
| Ghana SSNIT Remittance | SSNIT pension contribution schedule |

### Ivory Coast (2 reports)
| Report | Purpose |
|--------|---------|
| Ivory Coast ITS Remittance | Monthly ITS salary tax return |
| Ivory Coast CNPS Remittance | CNPS social security schedule |

### Egypt (2 reports)
| Report | Purpose |
|--------|---------|
| Egypt Income Tax Return | Monthly income tax return |
| Egypt Social Insurance Remittance | Social insurance contribution schedule |

### Morocco (2 reports)
| Report | Purpose |
|--------|---------|
| Morocco IR Remittance | Monthly IR salary tax return |
| Morocco CNSS Remittance | CNSS social security schedule |

### Tunisia (2 reports)
| Report | Purpose |
|--------|---------|
| Tunisia IRPP Remittance | Monthly IRPP salary tax return |
| Tunisia CNSS Remittance | CNSS social security schedule |

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
├── calculators/          # Country-specific calculator classes
│   ├── base.py           #   BaseCalculator (abstract)
│   ├── kenya.py          #   KenyaCalculator
│   ├── uganda.py         #   UgandaCalculator
│   └── ...               #   (20 countries total)
├── engine/
│   ├── hooks.py          # Salary Slip validate hook
│   └── registry.py       # Country → Calculator mapping + caching
├── boot.py               # extend_bootinfo (enabled countries → frappe.boot)
├── api.py                # Whitelisted API endpoints
├── tasks.py              # Scheduler tasks (yearly rate-review email)
├── setup.py              # after_install / after_migrate / before_uninstall
├── hooks.py              # App hooks, scheduler_events, fixtures config
├── payroll_africa/
│   ├── doctype/
│   │   ├── payroll_africa_settings/   # Global settings (SingleDocType, 20 country toggles)
│   │   ├── kenya_payroll_settings/    # Country settings (×20)
│   │   └── kenya_paye_band/           # PAYE/tax band child table (×20)
│   ├── report/                        # 51 reports (5 cross-country + 46 country-specific)
│   ├── print_format/                  # Salary Slip Africa Standard
│   └── workspace/                     # Workspace definition
├── workspace_sidebar/    # Sidebar template (filtered by enabled countries at runtime)
├── change_log/           # Release notes (shown in What's New dialog)
├── fixtures/             # Custom fields + Income Tax Slabs (20 countries)
├── public/
│   ├── css/              # Sidebar icon + change log styling
│   ├── js/
│   │   ├── payroll_africa_change_log.js      # What's New dialog renderer
│   │   ├── payroll_africa_salary_structure.js # Component dropdown filter
│   │   └── payroll_africa_sidebar.js         # Dynamic sidebar hide/show
│   └── icons/            # Africa SVG icon
├── demo/                 # Demo data setup/teardown
└── tests/                # Calculator unit tests (×20)
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

The registry (`engine/registry.py`) maps country names to calculator classes and caches instances for performance.

---

## Adding a New Country

1. **Create the calculator** — `calculators/newcountry.py` extending `BaseCalculator`
2. **Create the Settings DocType** — "New Country Payroll Settings" (SingleDocType) with rate fields and PAYE bands table
3. **Create the PAYE Band DocType** — "New Country PAYE Band" (child table)
4. **Register in registry.py** — add entries to `_country_map` and `_settings_map`
5. **Register in boot.py** — add entry to `COUNTRY_FIELD_MAP`
6. **Add setup function** — in `setup.py`, create settings, salary components, income tax slab, salary structure
7. **Add checkbox** — add `enable_newcountry` field to `payroll_africa_settings.json`
8. **Add sidebar items** — add settings link and reports section to `workspace_sidebar/payroll_africa.json`
9. **Create reports** — country-specific PAYE return and remittance reports
10. **Run `bench migrate`**

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

Each country has its own test file in `tests/` (20 total) that validates the calculator against known inputs and expected outputs.

---

## License

GPL-3.0
