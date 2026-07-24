# API Reference

All endpoints are `@frappe.whitelist()` decorated and accessible over REST.

## `calculate_deductions`

Compute deductions for any country without creating a Salary Slip — useful for simulations and what-if analysis.

```python
from payroll_africa.api import calculate_deductions

result = calculate_deductions("Kenya", gross_pay=100000)
# {
#   "country": "Kenya",
#   "gross_pay": 100000.0,
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

## `get_supported_countries`

Return the sorted list of all 54 supported country names.

## `recalculate_salary_slips`

Recalculate all **draft** Salary Slips for a single country in a date range.

```python
from payroll_africa.api import recalculate_salary_slips

result = recalculate_salary_slips("Kenya", "2025-01-01", "2025-12-31", company="My Co")
# {"updated": 42, "errors": [], "message": "42 salary slip(s) recalculated"}
```

## `recalculate_all_countries`

Recalculate draft slips for every enabled country in one call.

```python
from payroll_africa.api import recalculate_all_countries

result = recalculate_all_countries("2025-01-01", "2025-12-31")
# {
#   "updated": 142,
#   "by_country": {"Kenya": {...}, "Uganda": {...}, ...},
#   "message": "142 salary slip(s) recalculated across 5 countries"
# }
```

## REST examples

```bash
curl -X POST https://your-site/api/method/payroll_africa.api.calculate_deductions \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d '{"country": "Kenya", "gross_pay": 100000}'

curl -X POST https://your-site/api/method/payroll_africa.api.recalculate_all_countries \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d '{"from_date": "2025-01-01", "to_date": "2025-12-31"}'
```

## Next Steps

Developers extending Payroll Africa should read [Adding a New Country](adding-a-country.md).
