# Remaining Demo Data to Add

## Status
- COMPANIES dict: UPDATED with all 11 companies (done)
- All other dicts (CUSTOMERS, SUPPLIERS, BANKS, EMPLOYEES, SALARIES, STRUCTURE_DEDUCTIONS, TAX_SLABS, INVOICE_MULTIPLIERS): NEED 7 new entries each

## What needs to be added to setup_demo_data.py

### CUSTOMERS - add after Angola:
```python
    "Demo Tanzania":   ["Vodacom Tanzania", "CRDB Bank", "Tanzania Breweries", "Airtel Tanzania", "NMB Bank TZ"],
    "Demo Rwanda":     ["MTN Rwanda", "Bank of Kigali", "Bralirwa", "Airtel Rwanda", "I&M Bank Rwanda"],
    "Demo Zambia":     ["Zambia Sugar", "Zanaco Bank", "Airtel Zambia", "Zambeef Products", "Stanbic Zambia"],
    "Demo Mozambique": ["Mozal Aluminium", "BCI Mozambique", "Cervejas de Mocambique", "Vodacom Mozambique", "TDM Telecomunicacoes"],
    "Demo Malawi":     ["Illovo Sugar Malawi", "National Bank of Malawi", "Airtel Malawi", "Press Corporation", "FDH Bank Malawi"],
    "Demo DRC":        ["Rawbank DRC", "Vodacom Congo", "Brasimba SARL", "Orange RDC", "Equity BCDC"],
    "Demo Burundi":    ["Brarudi SA", "Econet Leo Burundi", "Interbank Burundi", "SOSUMO Burundi", "KCB Burundi"],
```

### SUPPLIERS - add after Angola:
```python
    "Demo Tanzania":   ["Dar Uniforms TZ", "Safari Fleet TZ", "Halotel Business", "SecureKit Tanzania", "CleanPro Tanzania"],
    "Demo Rwanda":     ["Kigali Uniforms", "RwandAir Fleet", "MTN Rwanda Biz", "SafeGuard Rwanda", "CleanServ Rwanda"],
    "Demo Zambia":     ["Lusaka Security Supplies", "Zambia Fleet Hire", "MTN Zambia Biz", "GuardTech Zambia", "CleanZam Services"],
    "Demo Mozambique": ["Maputo Tactical", "Mocambique Fleet", "Tmcel Business", "Seguranca Maputo", "Limpeza Mocambique"],
    "Demo Malawi":     ["Lilongwe Supplies", "Malawi Fleet Services", "TNM Business MW", "GuardForce Malawi", "CleanTech Malawi"],
    "Demo DRC":        ["Kinshasa Security Equip", "Congo Fleet Hire", "Vodacom Congo Biz", "Securite Kinshasa", "Proprete Congo"],
    "Demo Burundi":    ["Bujumbura Supplies", "Burundi Fleet Lease", "Lumitel Business", "SecureForce Burundi", "NettService Burundi"],
```

### BANKS - add after Angola:
```python
    "Demo Tanzania":   {"bank": "CRDB Bank Tanzania",    "account_name": "CRDB Main Account"},
    "Demo Rwanda":     {"bank": "Bank of Kigali",        "account_name": "BK Main Account"},
    "Demo Zambia":     {"bank": "Zanaco Bank",           "account_name": "Zanaco Main Account"},
    "Demo Mozambique": {"bank": "BCI Mozambique",        "account_name": "BCI Main Account"},
    "Demo Malawi":     {"bank": "National Bank Malawi",  "account_name": "NBM Main Account"},
    "Demo DRC":        {"bank": "Rawbank",               "account_name": "Rawbank Main Account"},
    "Demo Burundi":    {"bank": "Interbank Burundi",     "account_name": "Interbank Main Account"},
```

### EMPLOYEES - add after Angola:
```python
    "Demo Tanzania": [
        ("Baraka", "Mwakaje", "Male", "1982-05-10"),
        ("Neema", "Kimaro", "Female", "1986-09-14"),
        ("Juma", "Msuya", "Male", "1990-03-28"),
        ("Amina", "Shayo", "Female", "1991-12-02"),
        ("Hassan", "Mwendapole", "Male", "1987-07-19"),
    ],
    "Demo Rwanda": [
        ("Jean", "Habimana", "Male", "1983-02-25"),
        ("Claudine", "Uwimana", "Female", "1987-06-11"),
        ("Patrick", "Niyonzima", "Male", "1989-10-05"),
        ("Diane", "Mukamana", "Female", "1992-04-17"),
        ("Emmanuel", "Nsengiyumva", "Male", "1986-08-30"),
    ],
    "Demo Zambia": [
        ("Bwalya", "Mulenga", "Male", "1981-11-08"),
        ("Chanda", "Phiri", "Female", "1985-04-22"),
        ("Mwamba", "Kapasa", "Male", "1990-07-15"),
        ("Mutinta", "Banda", "Female", "1993-01-28"),
        ("Chilufya", "Tembo", "Male", "1988-09-12"),
    ],
    "Demo Mozambique": [
        ("Alberto", "Machava", "Male", "1982-08-20"),
        ("Fatima", "Sitoe", "Female", "1986-12-05"),
        ("Joaquim", "Cossa", "Male", "1991-02-18"),
        ("Celeste", "Mondlane", "Female", "1992-06-30"),
        ("Tomas", "Maluana", "Male", "1985-10-14"),
    ],
    "Demo Malawi": [
        ("Kondwani", "Chirwa", "Male", "1983-04-12"),
        ("Tadala", "Phiri", "Female", "1987-08-25"),
        ("Chisomo", "Banda", "Male", "1990-11-07"),
        ("Thandiwe", "Mbewe", "Female", "1992-03-19"),
        ("Limbani", "Nyirenda", "Male", "1986-06-01"),
    ],
    "Demo DRC": [
        ("Patient", "Kabongo", "Male", "1982-01-15"),
        ("Esperance", "Mutombo", "Female", "1986-05-28"),
        ("Fiston", "Kalala", "Male", "1989-09-10"),
        ("Grace", "Ilunga", "Female", "1991-07-22"),
        ("Olivier", "Tshimanga", "Male", "1987-12-04"),
    ],
    "Demo Burundi": [
        ("Janvier", "Ndayishimiye", "Male", "1983-06-18"),
        ("Claudette", "Niyonkuru", "Female", "1987-10-03"),
        ("Pacifique", "Bizimana", "Male", "1990-02-14"),
        ("Odette", "Hakizimana", "Female", "1992-08-26"),
        ("Aimable", "Niyongabo", "Male", "1986-04-08"),
    ],
```

### SALARIES - add after Angola (scaled to local currency):
```python
    "Demo Tanzania":   [1200000, 950000, 650000, 500000, 400000],
    "Demo Rwanda":     [800000, 600000, 400000, 300000, 250000],
    "Demo Zambia":     [25000, 20000, 14000, 10000, 8000],
    "Demo Mozambique": [120000, 95000, 65000, 50000, 40000],
    "Demo Malawi":     [800000, 600000, 400000, 300000, 250000],
    "Demo DRC":        [2500000, 2000000, 1400000, 1000000, 800000],
    "Demo Burundi":    [1500000, 1200000, 800000, 600000, 500000],
```

### STRUCTURE_DEDUCTIONS - add after Angola:
```python
    "Demo Tanzania":   ["PAYE TZ", "NSSF Employee TZ", "NSSF Employer TZ", "SDL", "WCF"],
    "Demo Rwanda":     ["PAYE RW", "Pension Employee RW", "Pension Employer RW", "Maternity Employee RW", "Maternity Employer RW", "CBHI RW", "Occupational Hazards RW"],
    "Demo Zambia":     ["PAYE ZM", "NAPSA Employee ZM", "NAPSA Employer ZM", "NHIMA Employee ZM", "NHIMA Employer ZM"],
    "Demo Mozambique": ["PAYE MZ", "INSS Employee MZ", "INSS Employer MZ"],
    "Demo Malawi":     ["PAYE MW", "Pension Employee MW", "Pension Employer MW"],
    "Demo DRC":        ["PAYE CD", "INSS Pension Employee CD", "INSS Pension Employer CD", "INSS Family Benefits CD", "INSS Occupational Risks CD", "INPP CD", "ONEM CD"],
    "Demo Burundi":    ["PAYE BI", "INSS Employee BI", "INSS Employer BI", "Health Insurance Employee BI", "Health Insurance Employer BI", "Training Fund Employee BI", "Training Fund Employer BI", "Work Injury BI"],
```

### TAX_SLABS - add after Angola:
```python
    "Demo Tanzania":   "Tanzania PAYE 2025",
    "Demo Rwanda":     "Rwanda PAYE 2025",
    "Demo Zambia":     "Zambia PAYE 2025",
    "Demo Mozambique": "Mozambique PAYE 2025",
    "Demo Malawi":     "Malawi PAYE 2025",
    "Demo DRC":        "DRC PAYE 2025",
    "Demo Burundi":    "Burundi PAYE 2025",
```

### INVOICE_MULTIPLIERS - add after AOA:
```python
    "TZS": 20,
    "RWF": 8,
    "ZMW": 0.2,
    "MZN": 0.5,
    "MWK": 12,
    "CDF": 20,
    "BIF": 20,
```

## Also needs:
1. Add new companies to FY 2026 (update _ensure_fiscal_year or add them manually)
2. Run: `bench --site <your-site> execute payroll_africa.demo.setup_demo_data.execute`
   - The script is idempotent; it skips already-created records for the original 4 companies

## Quick execution steps for next session:
1. Read this file
2. Add all the data blocks above to setup_demo_data.py (after existing entries in each dict)
3. Add new companies to FY 2026:
   ```
   bench --site <your-site> console
   fy = frappe.get_doc("Fiscal Year", "2026")
   for c in ["Demo Tanzania","Demo Rwanda","Demo Zambia","Demo Mozambique","Demo Malawi","Demo DRC","Demo Burundi"]:
       fy.append("companies", {"company": c})
   fy.save(ignore_permissions=True)
   frappe.db.commit()
   ```
4. Clear cache: `bench --site <your-site> clear-cache`
5. Run: `bench --site <your-site> execute payroll_africa.demo.setup_demo_data.execute`
