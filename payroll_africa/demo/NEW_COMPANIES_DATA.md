# Remaining Demo Data to Add

## Status
- COMPANIES dict: UPDATED with all 11 companies (done)
- All other dicts (CUSTOMERS, SUPPLIERS, BANKS, EMPLOYEES, SALARIES, STRUCTURE_DEDUCTIONS, TAX_SLABS, INVOICE_MULTIPLIERS): NEED 7 new entries each

## What needs to be added to setup_demo_data.py

### CUSTOMERS - add after Angola:
```python
    "Garda Tanzania":   ["Vodacom Tanzania", "CRDB Bank", "Tanzania Breweries", "Airtel Tanzania", "NMB Bank TZ"],
    "GARDA RWANDA":     ["MTN Rwanda", "Bank of Kigali", "Bralirwa", "Airtel Rwanda", "I&M Bank Rwanda"],
    "Garda Zambia":     ["Zambia Sugar", "Zanaco Bank", "Airtel Zambia", "Zambeef Products", "Stanbic Zambia"],
    "Garda Mozambique": ["Mozal Aluminium", "BCI Mozambique", "Cervejas de Mocambique", "Vodacom Mozambique", "TDM Telecomunicacoes"],
    "Garda Malawi":     ["Illovo Sugar Malawi", "National Bank of Malawi", "Airtel Malawi", "Press Corporation", "FDH Bank Malawi"],
    "Garda DRC":        ["Rawbank DRC", "Vodacom Congo", "Brasimba SARL", "Orange RDC", "Equity BCDC"],
    "Garda Burundi":    ["Brarudi SA", "Econet Leo Burundi", "Interbank Burundi", "SOSUMO Burundi", "KCB Burundi"],
```

### SUPPLIERS - add after Angola:
```python
    "Garda Tanzania":   ["Dar Uniforms TZ", "Safari Fleet TZ", "Halotel Business", "SecureKit Tanzania", "CleanPro Tanzania"],
    "GARDA RWANDA":     ["Kigali Uniforms", "RwandAir Fleet", "MTN Rwanda Biz", "SafeGuard Rwanda", "CleanServ Rwanda"],
    "Garda Zambia":     ["Lusaka Security Supplies", "Zambia Fleet Hire", "MTN Zambia Biz", "GuardTech Zambia", "CleanZam Services"],
    "Garda Mozambique": ["Maputo Tactical", "Mocambique Fleet", "Tmcel Business", "Seguranca Maputo", "Limpeza Mocambique"],
    "Garda Malawi":     ["Lilongwe Supplies", "Malawi Fleet Services", "TNM Business MW", "GuardForce Malawi", "CleanTech Malawi"],
    "Garda DRC":        ["Kinshasa Security Equip", "Congo Fleet Hire", "Vodacom Congo Biz", "Securite Kinshasa", "Proprete Congo"],
    "Garda Burundi":    ["Bujumbura Supplies", "Burundi Fleet Lease", "Lumitel Business", "SecureForce Burundi", "NettService Burundi"],
```

### BANKS - add after Angola:
```python
    "Garda Tanzania":   {"bank": "CRDB Bank Tanzania",    "account_name": "CRDB Main Account"},
    "GARDA RWANDA":     {"bank": "Bank of Kigali",        "account_name": "BK Main Account"},
    "Garda Zambia":     {"bank": "Zanaco Bank",           "account_name": "Zanaco Main Account"},
    "Garda Mozambique": {"bank": "BCI Mozambique",        "account_name": "BCI Main Account"},
    "Garda Malawi":     {"bank": "National Bank Malawi",  "account_name": "NBM Main Account"},
    "Garda DRC":        {"bank": "Rawbank",               "account_name": "Rawbank Main Account"},
    "Garda Burundi":    {"bank": "Interbank Burundi",     "account_name": "Interbank Main Account"},
```

### EMPLOYEES - add after Angola:
```python
    "Garda Tanzania": [
        ("Baraka", "Mwakaje", "Male", "1982-05-10"),
        ("Neema", "Kimaro", "Female", "1986-09-14"),
        ("Juma", "Msuya", "Male", "1990-03-28"),
        ("Amina", "Shayo", "Female", "1991-12-02"),
        ("Hassan", "Mwendapole", "Male", "1987-07-19"),
    ],
    "GARDA RWANDA": [
        ("Jean", "Habimana", "Male", "1983-02-25"),
        ("Claudine", "Uwimana", "Female", "1987-06-11"),
        ("Patrick", "Niyonzima", "Male", "1989-10-05"),
        ("Diane", "Mukamana", "Female", "1992-04-17"),
        ("Emmanuel", "Nsengiyumva", "Male", "1986-08-30"),
    ],
    "Garda Zambia": [
        ("Bwalya", "Mulenga", "Male", "1981-11-08"),
        ("Chanda", "Phiri", "Female", "1985-04-22"),
        ("Mwamba", "Kapasa", "Male", "1990-07-15"),
        ("Mutinta", "Banda", "Female", "1993-01-28"),
        ("Chilufya", "Tembo", "Male", "1988-09-12"),
    ],
    "Garda Mozambique": [
        ("Alberto", "Machava", "Male", "1982-08-20"),
        ("Fatima", "Sitoe", "Female", "1986-12-05"),
        ("Joaquim", "Cossa", "Male", "1991-02-18"),
        ("Celeste", "Mondlane", "Female", "1992-06-30"),
        ("Tomas", "Maluana", "Male", "1985-10-14"),
    ],
    "Garda Malawi": [
        ("Kondwani", "Chirwa", "Male", "1983-04-12"),
        ("Tadala", "Phiri", "Female", "1987-08-25"),
        ("Chisomo", "Banda", "Male", "1990-11-07"),
        ("Thandiwe", "Mbewe", "Female", "1992-03-19"),
        ("Limbani", "Nyirenda", "Male", "1986-06-01"),
    ],
    "Garda DRC": [
        ("Patient", "Kabongo", "Male", "1982-01-15"),
        ("Esperance", "Mutombo", "Female", "1986-05-28"),
        ("Fiston", "Kalala", "Male", "1989-09-10"),
        ("Grace", "Ilunga", "Female", "1991-07-22"),
        ("Olivier", "Tshimanga", "Male", "1987-12-04"),
    ],
    "Garda Burundi": [
        ("Janvier", "Ndayishimiye", "Male", "1983-06-18"),
        ("Claudette", "Niyonkuru", "Female", "1987-10-03"),
        ("Pacifique", "Bizimana", "Male", "1990-02-14"),
        ("Odette", "Hakizimana", "Female", "1992-08-26"),
        ("Aimable", "Niyongabo", "Male", "1986-04-08"),
    ],
```

### SALARIES - add after Angola (scaled to local currency):
```python
    "Garda Tanzania":   [1200000, 950000, 650000, 500000, 400000],
    "GARDA RWANDA":     [800000, 600000, 400000, 300000, 250000],
    "Garda Zambia":     [25000, 20000, 14000, 10000, 8000],
    "Garda Mozambique": [120000, 95000, 65000, 50000, 40000],
    "Garda Malawi":     [800000, 600000, 400000, 300000, 250000],
    "Garda DRC":        [2500000, 2000000, 1400000, 1000000, 800000],
    "Garda Burundi":    [1500000, 1200000, 800000, 600000, 500000],
```

### STRUCTURE_DEDUCTIONS - add after Angola:
```python
    "Garda Tanzania":   ["PAYE TZ", "NSSF Employee TZ", "NSSF Employer TZ", "SDL", "WCF"],
    "GARDA RWANDA":     ["PAYE RW", "Pension Employee RW", "Pension Employer RW", "Maternity Employee RW", "Maternity Employer RW", "CBHI RW", "Occupational Hazards RW"],
    "Garda Zambia":     ["PAYE ZM", "NAPSA Employee ZM", "NAPSA Employer ZM", "NHIMA Employee ZM", "NHIMA Employer ZM"],
    "Garda Mozambique": ["PAYE MZ", "INSS Employee MZ", "INSS Employer MZ"],
    "Garda Malawi":     ["PAYE MW", "Pension Employee MW", "Pension Employer MW"],
    "Garda DRC":        ["PAYE CD", "INSS Pension Employee CD", "INSS Pension Employer CD", "INSS Family Benefits CD", "INSS Occupational Risks CD", "INPP CD", "ONEM CD"],
    "Garda Burundi":    ["PAYE BI", "INSS Employee BI", "INSS Employer BI", "Health Insurance Employee BI", "Health Insurance Employer BI", "Training Fund Employee BI", "Training Fund Employer BI", "Work Injury BI"],
```

### TAX_SLABS - add after Angola:
```python
    "Garda Tanzania":   "Tanzania PAYE 2025",
    "GARDA RWANDA":     "Rwanda PAYE 2025",
    "Garda Zambia":     "Zambia PAYE 2025",
    "Garda Mozambique": "Mozambique PAYE 2025",
    "Garda Malawi":     "Malawi PAYE 2025",
    "Garda DRC":        "DRC PAYE 2025",
    "Garda Burundi":    "Burundi PAYE 2025",
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
2. Run: `bench --site gardaworld execute payroll_africa.demo.setup_demo_data.execute`
   - The script is idempotent; it skips already-created records for the original 4 companies

## Quick execution steps for next session:
1. Read this file
2. Add all the data blocks above to setup_demo_data.py (after existing entries in each dict)
3. Add new companies to FY 2026:
   ```
   bench --site gardaworld console
   fy = frappe.get_doc("Fiscal Year", "2026")
   for c in ["Garda Tanzania","GARDA RWANDA","Garda Zambia","Garda Mozambique","Garda Malawi","Garda DRC","Garda Burundi"]:
       fy.append("companies", {"company": c})
   fy.save(ignore_permissions=True)
   frappe.db.commit()
   ```
4. Clear cache: `bench --site gardaworld clear-cache`
5. Run: `bench --site gardaworld execute payroll_africa.demo.setup_demo_data.execute`
