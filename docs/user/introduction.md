# Introduction

Payroll Africa is an open-source app that automates statutory payroll deductions across **all 54 African countries** on ERPNext and Frappe HR. It computes employee and employer statutory contributions — PAYE, social security, health insurance, housing levies, training funds, and pension — on every Salary Slip, using each country's current tax bands and rates.

No manual calculation. No spreadsheets. Change a rate in settings, and the next payroll run picks it up.

![Payroll Africa workspace](screenshots/workspace.png)

## Why Payroll Africa

Payroll teams across Africa maintain 54 different statutory rulebooks by hand, and those rates change every year. Getting them wrong means penalties from the revenue authority.

- Payroll Africa brings every country's statutory logic into one app, wired directly into the Frappe HR payroll engine.
- Rates and tax bands are configurable from the UI with effective dates — no code changes, no redeployment.
- Enable only the countries you operate in; the rest stay out of your way.

## Key Features

- **Automatic deduction computation** on every Salary Slip via the Frappe HR `apply_regional_deductions` regional hook.
- **54 countries** — a dedicated calculator, configurable Settings page, and tax-band table for each.
- **111 reports** — country-specific PAYE returns and social-security remittances, plus cross-country summaries.
- **Country enable/disable** — toggle active countries from a single settings page; the sidebar and salary-component dropdowns update automatically.
- **Automatic country detection** — countries are enabled automatically from your Company records, on install and whenever a Company is added.
- **Rate-change tracking** — update statutory rates with effective dates, backed by an audit-trail report.
- **Salary structure templates & income tax slabs** — pre-built for every country with statutory deductions.
- **Standalone deduction API** — calculate deductions for any country without creating a Salary Slip.
- **Bulk recalculation** — recompute all enabled countries' draft slips in one call.

## Supported Regions

| Region | Countries |
|--------|-----------|
| East Africa | Kenya, Uganda, Tanzania, Rwanda, Burundi, Ethiopia, Djibouti, Eritrea, Somalia, South Sudan, Sudan |
| Southern Africa | Malawi, Zambia, Mozambique, Angola, Botswana, South Africa, Namibia, Madagascar, Zimbabwe, Lesotho, Eswatini |
| West Africa | Nigeria, Ghana, Ivory Coast, Senegal, Mali, Niger, Burkina Faso, Benin, Togo, Guinea, Sierra Leone, Liberia, Gambia, Guinea-Bissau, Cabo Verde, Mauritania |
| North Africa | Egypt, Morocco, Tunisia, Algeria, Libya |
| Central Africa | DRC, Cameroon, Gabon, Congo, CAR, Chad, Equatorial Guinea, Sao Tome and Principe, Comoros |
| Indian Ocean | Mauritius, Seychelles, Madagascar |

## Under the Hood

- **[Frappe Framework](https://github.com/frappe/frappe)** — the full-stack Python/JavaScript web framework Payroll Africa is built on.
- **[Frappe HR (HRMS)](https://github.com/frappe/hrms)** — Payroll Africa extends the Salary Slip payroll engine through its supported regional-override hook, without patching core.
- **[ERPNext](https://github.com/frappe/erpnext)** — provides the accounting, company, and currency foundations.

## Next Steps

1. [Installation](installation.md)
2. [Getting Started](getting-started.md)
3. [Country Settings](country-settings.md)
4. [Running Payroll](running-payroll.md)
5. [Reports](reports.md)
6. [API Reference](api.md)
7. [Adding a New Country](adding-a-country.md)
