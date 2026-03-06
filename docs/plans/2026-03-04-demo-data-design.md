# Demo Data Setup Design

**Date:** 2026-03-04
**Purpose:** Create realistic sample data across 4 GardaWorld country companies for testing payroll_africa

## Companies (existing)

| Company | Country | Currency | Abbr |
|---|---|---|---|
| Garda Kenya | Kenya | KES | GK |
| Garda Uganda | Uganda | UGX | GU |
| Garda Nigeria | Nigeria | NGN | GN |
| Garda Angola | Angola | AOA | GA |

## 1. Items (5 service items, shared)

| Item Code | Item Name | Item Group |
|---|---|---|
| SVC-GUARD | Armed Guarding Services | Services |
| SVC-ESCORT | Executive Protection & Escort | Services |
| SVC-CONSULT | Risk Consulting | Services |
| SVC-CIT | Cash-in-Transit | Services |
| SVC-SURVEIL | Surveillance & Monitoring | Services |

All non-stock, service type.

## 2. Customers (5 per company = 20 total)

| Kenya | Uganda | Nigeria | Angola |
|---|---|---|---|
| Safaricom PLC | MTN Uganda | Dangote Group | Sonangol EP |
| Kenya Airways | Stanbic Uganda | Shell Nigeria | BAI Angola |
| East African Breweries | Umeme Ltd | Access Bank | Unitel Angola |
| Equity Bank Kenya | Airtel Uganda | Total Energies NG | Porto de Luanda |
| KenGen | Uganda Breweries | Nigerian Breweries | TAAG Airlines |

Each customer linked to the corresponding company's territory/country.

## 3. Suppliers (5 per company = 20 total)

| Kenya | Uganda | Nigeria | Angola |
|---|---|---|---|
| Safeguard Supplies KE | Kampala Uniforms | Abuja Security Equip | Luanda Tactical |
| Nairobi Fleet Leasing | Entebbe Transport | Lagos Vehicle Hire | Sonangol Fuel |
| Telkom Kenya | Airtel Uganda Biz | MTN Nigeria Biz | Movicel Business |
| KK Security Supplies | Pearl Uniforms UG | Hallmark Security NG | Segurança Supplies |
| Nelly's Cleaning KE | Cleantek Uganda | CleanServ Nigeria | Limpeza Angola |

## 4. Bank Accounts (1 per company)

| Company | Bank Name | Account Name |
|---|---|---|
| Garda Kenya | Kenya Commercial Bank | KCB Main Account |
| Garda Uganda | Standard Chartered Uganda | StanChart Main Account |
| Garda Nigeria | First Bank Nigeria | FirstBank Main Account |
| Garda Angola | Banco BAI | BAI Main Account |

Creates Bank doctype, Bank Account doctype, and GL Account under "Bank Accounts - XX".

## 5. Employees (5 per company = 20 total)

| Role | Kenya (KES) | Uganda (UGX) | Nigeria (NGN) | Angola (AOA) |
|---|---|---|---|---|
| Country Manager | 150,000 | 4,000,000 | 900,000 | 500,000 |
| Operations Lead | 120,000 | 3,000,000 | 700,000 | 400,000 |
| Senior Guard | 80,000 | 2,000,000 | 500,000 | 280,000 |
| Guard | 60,000 | 1,800,000 | 350,000 | 200,000 |
| Driver | 50,000 | 1,500,000 | 300,000 | 150,000 |

Employee settings: date_of_joining=2025-01-01, payroll_country set, status=Active.

## 6. Salary Structures (1 per company)

New salary structures per company with:
- Earning: Basic Salary (formula-based or fixed)
- Deductions: auto-calculated by payroll_africa engine hook on validate

## 7. Payroll Processing (January 2026)

Per company:
1. Create Payroll Period: Jan 1 2026 - Dec 31 2026
2. Create Salary Structure Assignment for each employee (from_date=2026-01-01)
3. Create Payroll Entry for Jan 1-31, 2026
4. Get salary slip entries, submit slips

## 8. Sales & Purchase Invoices (5 each per company)

- Sales: one per customer, different service items, realistic local-currency amounts
- Purchase: one per supplier, equipment/services procurement
- All dated January 2026, submitted

## Script

```
apps/payroll_africa/payroll_africa/demo/
├── __init__.py
└── setup_demo_data.py
```

Run: `bench --site gardaworld execute payroll_africa.demo.setup_demo_data.execute`
Teardown: `bench --site gardaworld execute payroll_africa.demo.setup_demo_data.teardown`
