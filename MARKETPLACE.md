# Payroll Africa

Statutory payroll deduction automation for **54 African countries**, built on Frappe + HRMS.

Payroll Africa hooks into HRMS Salary Slip validation to automatically compute employee and employer statutory deductions — PAYE, social security, health insurance, housing levies, training funds, and pension contributions — using each country's current tax bands and rates. No manual calculation, no spreadsheets: change a rate in settings and the next payroll run picks it up.

> This file is the canonical **Frappe Cloud Marketplace "Long Description"** source. It deliberately contains **no installation commands** (no `get-app`, `install-app`, or migration commands), which the marketplace metadata check rejects. Paste it into the listing's Long Description field, or sync the listing from it.

## Key Features

- Automatic deduction computation on every Salary Slip via the HRMS `apply_regional_deductions` regional override
- 54 countries — 54 calculators, 54 configurable Settings pages, 54 tax-band tables
- 111 reports — country-specific PAYE returns, social-security remittances, plus 5 cross-country reports
- Country enable/disable — toggle active countries from a single settings page; sidebar and component dropdowns update automatically
- Rate-change tracking with effective dates and an audit-trail report
- Pre-built salary structures and income tax slabs for every country with statutory deductions (44 countries)
- Standalone deduction API for simulations and what-if analysis
- Bulk recalculation across all enabled countries
- Yearly rate-review reminder for Payroll Managers
- Espresso-aligned "What's New" release notes and payslip print format
- 347 unit tests, all passing

## How It Works

Each employee's payroll country is resolved from the Salary Structure Assignment, Employee, or Company. The matching country calculator loads current rates from that country's Settings page and computes deductions using its tax bands, ceilings, and formulas. Employee deductions populate the Salary Slip deductions table; employer-only contributions populate the employer-contributions table. If a country's settings are unconfigured, calculators fall back to current statutory defaults so payroll works immediately.

## Installation

Available on the Frappe Cloud Marketplace. ERPNext and HRMS are provisioned automatically as dependencies.

## License

GPL-3.0
