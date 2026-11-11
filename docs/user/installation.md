# Installation

## Prerequisites

- Frappe Framework v15 or v16
- ERPNext
- Frappe HR (HRMS)

> **Important:** Payroll Africa computes deductions through Frappe HR's `apply_regional_deductions` regional hook on the Salary Slip. On HRMS versions that do not yet expose this hook, install a build that includes it (see the [upstream hook PR](../upstream/hrms-pr-body.md)). Without the hook, the calculators still work through the [standalone API](api.md), but deductions will not populate automatically on Salary Slips.

## Install from the Frappe Cloud Marketplace

Add **Payroll Africa** to your bench from the Frappe Cloud Marketplace. ERPNext and Frappe HR are provisioned automatically as dependencies.

## Install on a self-hosted bench

```bash
bench get-app https://github.com/CoaleTech/payroll_africa
bench --site your-site.local install-app payroll_africa
```

## What installation provisions

On install, Payroll Africa sets up:

- **Currency records** for all required currencies.
- **`Employee.payroll_country`** custom Link field (to the standard Country DocType).
- **Country-specific Salary Components** for each deduction type.
- **Configurable Settings DocTypes** with current statutory tax bands for all 54 countries.
- **Income Tax Slabs and Salary Structure templates** for every country with statutory deductions (44 countries).
- **A workspace** with country sections and reports, plus a Desktop icon under Frappe HR.

> Somalia and South Sudan have no mandatory statutory deductions (documented no-ops). Every other country exposes configurable rates and tax bands.

## Verify the installation

1. Open the **Payroll Africa** workspace from the desk sidebar.
2. Confirm **Payroll Africa Settings** opens and lists the enabled countries.
3. Open a country settings page (e.g. **Kenya Payroll Settings**) and confirm its rate fields and tax bands are populated.

## Uninstall

When the app is removed, its `before_uninstall` step cleans up the salary structures, salary components, income tax slabs, and custom fields it created.

```bash
bench --site your-site.local uninstall-app payroll_africa
```

## Next Steps

Continue to [Getting Started](getting-started.md).
