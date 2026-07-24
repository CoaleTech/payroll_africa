# Changelog

All notable changes to Payroll Africa are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive user documentation (`docs/user/`) with screenshots: introduction,
  installation, getting started, country settings, running payroll, reports, API
  reference, and adding a new country.
- Single-file comprehensive manual: `docs/payroll-africa-documentation.html` and
  an 8-page `docs/payroll-africa-documentation.pdf` with embedded screenshots.
- GitHub Actions CI (server tests on Frappe v16) and pre-commit linter workflows.
- README status badges (CI, tests, countries, license, Frappe version).
- Automatic country detection — Payroll Africa now enables the country of each
  Company automatically on install and on Company creation (additive; never
  disables manual choices), including Cape Verde/Swaziland country-name aliases.

### Changed
- Aligned publisher, author, and source copyright to CoaleTech
  (`support@coale.tech`) across `pyproject.toml`, `hooks.py`, and source headers.

## [0.0.3] - 2026-07-22

Full 54-country coverage — every country now ships with configurable statutory
settings, verified rates, and an Espresso-aligned UI.

### Added
- Per-country setup for the remaining regions: Central Africa (Cameroon, Gabon,
  Congo, CAR, Chad, Equatorial Guinea, Sao Tome), North Africa (Algeria, Libya,
  Sudan, Mauritania), East Africa (Djibouti, Eritrea, Comoros, Seychelles),
  Franco-West (Senegal, Mali, Niger, Burkina Faso, Benin, Togo, Guinea,
  Guinea-Bissau), West-Anglo (Sierra Leone, Liberia, Gambia, Cabo Verde,
  Mauritius) and Zimbabwe.
- All 54 countries provisioned with configurable Settings DocTypes and tax bands;
  44 ship pre-built Income Tax Slabs and Salary Structure templates.
- Togo INAM health contribution (employee + employer) with new settings fields.
- Documented no-op handling for Somalia and South Sudan (no mandatory statutory
  deductions).

### Changed
- Statutory rate corrections across ~30 countries, verified against PwC Worldwide
  Tax Summaries and national revenue authorities (Kenya NSSF ceiling, Zambia
  NAPSA cap, Egypt exemption, Tunisia CNSS, Morocco IR bands, Algeria IRG,
  Namibia SSC, Botswana PAYE, Burkina/Benin/Togo ceilings and PIT bands).
- 16 additional currency records added for the newly seeded countries.
- "What's New" dialog restyled to the Frappe Espresso design system with
  automatic light/dark theme support.
- Salary Slip Africa Standard print format aligned to the Espresso palette and
  Inter typography (PDF-safe literal values).

### Fixed
- Burkina Faso, Benin and Togo contribution ceilings and progressive
  PIT/IUTS/IRPP bands corrected.
- Namibia SSC annual ceiling synced between setup defaults and live settings.
- Change Log dialog dark-mode colors no longer hardcoded.

## [0.0.2] - 2026-07-17

Major architecture refactor aligning Payroll Africa with native HRMS patterns.

### Added
- HRMS `apply_regional_deductions` regional override for all 54 supported
  countries.
- `Salary Structure Assignment.payroll_country` field for date-effective country
  resolution.
- `payroll_africa.engine.utils.get_effective_ssa_values()` helper for
  assignment-level lookups.
- Employer-only statutory components now use the HRMS `Employer Contribution`
  component type.

### Changed
- Country resolution now prefers `Salary Structure Assignment.payroll_country`,
  then `Employee.payroll_country`, then `Company.country`.
- Employer contributions routed to the Salary Slip `employer_contributions`
  child table instead of statistical deduction rows.
- Salary Structure templates place employer components in the
  `employer_contributions` table.
- Setup patches type/statistical flags on existing Salary Components during
  migrate.

### Removed
- `Salary Slip.validate` doc_event hook (replaced by the HRMS regional override).

## [0.0.1] - 2026-07-12

Initial launch — statutory payroll deduction automation for 11 African countries.

### Added
- Automatic PAYE computation for 11 countries (Kenya, Uganda, Tanzania, Rwanda,
  Burundi, Zambia, Malawi, DRC, Nigeria, Mozambique, Angola).
- Country-specific salary components and income tax slabs.
- 15+ statutory reports (P9A, P10, URA PAYE Return, PenCom Remittance, and more).
- Salary Slip Africa Standard print format.
- Country enable/disable toggles in Payroll Africa Settings.
- Workspace sidebar and salary-component dropdowns dynamically filtered to
  enabled countries.

[Unreleased]: https://github.com/CoaleTech/payroll_africa/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/CoaleTech/payroll_africa/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/CoaleTech/payroll_africa/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/CoaleTech/payroll_africa/releases/tag/v0.0.1
