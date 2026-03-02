### Payroll Africa

Statutory payroll deduction automation for 11 African countries. Integrates with HRMS Salary Slip to automatically compute employee and employer statutory deductions.

### Supported Countries

| Country | Currency | Statutory Deductions |
|---------|----------|---------------------|
| Kenya | KES | PAYE, NSSF (Tier I & II), SHIF, Housing Levy, NITA |
| Uganda | UGX | PAYE, NSSF (5%/10%/15% tiers), LST |
| Tanzania | TZS | PAYE, NSSF, SDL, WCF |
| Rwanda | RWF | PAYE, Pension, Maternity, CBHI, Occupational Hazards |
| Burundi | BIF | PAYE, INSS, Work Injury, Health Insurance, Training Fund |
| Zambia | ZMW | PAYE, NAPSA (capped), NHIMA |
| Malawi | MWK | PAYE, Pension |
| DRC | CDF | PAYE/IPR, INSS Pension, Occupational Risks, Family Benefits, INPP, ONEM |
| Nigeria | NGN | PAYE, Pension, NHF, NHIS, NSITF, ITF |
| Mozambique | MZN | PAYE, INSS |
| Angola | AOA | PAYE/IRT, INSS |

### How It Works

1. **Install the app** - creates salary components, Income Tax Slabs, and template Salary Structures for all countries
2. **Set the employee's country** - use the "Payroll Country" field on Employee (falls back to Company country)
3. **Assign a salary structure** - use the country template (e.g. "Kenya Payroll Template") or create your own with the statutory components
4. **Process payroll** - when a Salary Slip is saved, the hook automatically computes all statutory deductions using the country's current rates

### Configuration

Each country has its own settings DocType (e.g. "Kenya Payroll Settings") where you can update statutory rates when legislation changes. Access these from the Payroll Africa workspace under Frappe HR.

### Reports

- **Statutory Deductions Summary** - all deductions by employee/period
- **Employer Contributions** - employer-only deductions
- **Cost to Company** - total compensation including employer contributions
- **P9A Tax Deduction Card** - Kenya statutory tax card
- **P10 Monthly Tax Return** - Kenya monthly PAYE return
- **NSSF Remittance** - Kenya NSSF report
- **SHIF Remittance** - Kenya health insurance report
- **Housing Levy Return** - Kenya housing levy report

### API

Calculate deductions without creating a Salary Slip:

```python
from payroll_africa.api import calculate_deductions
result = calculate_deductions("Kenya", gross_pay=100000)
# Returns: deductions list, employee_total, employer_total, net_pay, cost_to_company
```

Recalculate draft salary slips after rate changes:

```python
from payroll_africa.api import recalculate_salary_slips
result = recalculate_salary_slips("Kenya", "2025-01-01", "2025-12-31", company="My Company")
```

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app payroll_africa
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/payroll_africa
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

gpl-3.0
