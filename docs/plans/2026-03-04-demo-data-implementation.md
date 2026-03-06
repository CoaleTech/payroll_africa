# Demo Data Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a single Python script that populates 4 GardaWorld country companies with realistic demo data (customers, suppliers, employees, invoices, payroll).

**Architecture:** One `setup_demo_data.py` module with an `execute()` entry point that calls helper functions in dependency order: items → customers/suppliers → banks → employees → salary structures → salary assignments → payroll entries → invoices. A `teardown()` function deletes all demo data by tag prefix.

**Tech Stack:** Frappe Python API (`frappe.get_doc`, `frappe.get_all`), bench execute

---

## Context: Existing Site State

- **Site:** `gardaworld` (NOT `gardawarld`)
- **Companies:** Garda Kenya (GK/KES), Garda Uganda (GU/UGX), Garda Nigeria (GN/NGN), Garda Angola (GA/AOA)
- **Salary structures exist** for each country but ALL linked to Garda Kenya — we create NEW per-company structures
- **Salary components** already exist for all 4 countries (PAYE, NSSF, SHIF, etc.)
- **Income Tax Slabs** exist for all countries (e.g. "Kenya PAYE 2025")
- **Departments** exist per company (e.g. "Operations - GK", "Management - GK")
- **Designations** exist (Manager, Consultant, etc.)
- **Chart of Accounts** per company with: "Debtors - XX", "Creditors - XX", "Bank Accounts - XX", "Service - XX", "Cost of Goods Sold - XX"
- **Item Group** "Services" exists
- **No employees, no suppliers, no items, no payroll periods** yet (1 test customer "E2E Test Corp")
- **payroll_africa hook** auto-calculates statutory deductions on salary slip validate — salary structures just need Basic Salary earning + deduction placeholders at amount=0

## Data Constants

```python
COMPANIES = {
    "Garda Kenya":   {"abbr": "GK", "currency": "KES", "country": "Kenya"},
    "Garda Uganda":  {"abbr": "GU", "currency": "UGX", "country": "Uganda"},
    "Garda Nigeria": {"abbr": "GN", "currency": "NGN", "country": "Nigeria"},
    "Garda Angola":  {"abbr": "GA", "currency": "AOA", "country": "Angola"},
}

ITEMS = [
    {"item_code": "SVC-GUARD",    "item_name": "Armed Guarding Services"},
    {"item_code": "SVC-ESCORT",   "item_name": "Executive Protection & Escort"},
    {"item_code": "SVC-CONSULT",  "item_name": "Risk Consulting"},
    {"item_code": "SVC-CIT",      "item_name": "Cash-in-Transit"},
    {"item_code": "SVC-SURVEIL",  "item_name": "Surveillance & Monitoring"},
]

CUSTOMERS = {
    "Garda Kenya":   ["Safaricom PLC", "Kenya Airways", "East African Breweries", "Equity Bank Kenya", "KenGen"],
    "Garda Uganda":  ["MTN Uganda", "Stanbic Uganda", "Umeme Ltd", "Airtel Uganda", "Uganda Breweries"],
    "Garda Nigeria": ["Dangote Group", "Shell Nigeria", "Access Bank", "Total Energies NG", "Nigerian Breweries"],
    "Garda Angola":  ["Sonangol EP", "BAI Angola", "Unitel Angola", "Porto de Luanda", "TAAG Airlines"],
}

SUPPLIERS = {
    "Garda Kenya":   ["Safeguard Supplies KE", "Nairobi Fleet Leasing", "Telkom Kenya", "KK Security Supplies", "Nelly's Cleaning KE"],
    "Garda Uganda":  ["Kampala Uniforms", "Entebbe Transport", "Airtel Uganda Biz", "Pearl Uniforms UG", "Cleantek Uganda"],
    "Garda Nigeria": ["Abuja Security Equip", "Lagos Vehicle Hire", "MTN Nigeria Biz", "Hallmark Security NG", "CleanServ Nigeria"],
    "Garda Angola":  ["Luanda Tactical", "Sonangol Fuel", "Movicel Business", "Segurança Supplies", "Limpeza Angola"],
}

BANKS = {
    "Garda Kenya":   {"bank": "Kenya Commercial Bank",       "account_name": "KCB Main Account"},
    "Garda Uganda":  {"bank": "Standard Chartered Uganda",   "account_name": "StanChart Main Account"},
    "Garda Nigeria": {"bank": "First Bank Nigeria",          "account_name": "FirstBank Main Account"},
    "Garda Angola":  {"bank": "Banco BAI",                   "account_name": "BAI Main Account"},
}

# (first_name, last_name, gender, date_of_birth, designation)
EMPLOYEE_TEMPLATES = [
    ("James",  "Mwangi",   "Male",   "1980-03-15", "Manager",    "Management"),
    ("Grace",  "Ochieng",  "Female", "1985-07-22", "Consultant", "Operations"),
    ("Peter",  "Kamau",    "Male",   "1990-01-10", "Associate",  "Operations"),
    ("Mary",   "Wanjiku",  "Female", "1992-11-05", "Associate",  "Operations"),
    ("David",  "Oduor",    "Male",   "1988-06-18", "Associate",  "Operations"),
]

SALARIES = {
    "Garda Kenya":   [150000, 120000,  80000,  60000,  50000],
    "Garda Uganda":  [4000000, 3000000, 2000000, 1800000, 1500000],
    "Garda Nigeria": [900000, 700000, 500000, 350000, 300000],
    "Garda Angola":  [500000, 400000, 280000, 200000, 150000],
}

# Salary structure deduction components per country (already exist in site)
STRUCTURE_DEDUCTIONS = {
    "Garda Kenya":   ["PAYE", "NSSF Employee", "NSSF Employer", "SHIF", "Housing Levy", "Employer Housing Levy", "NITA"],
    "Garda Uganda":  ["PAYE UG", "NSSF Employee UG", "NSSF Employer UG", "LST"],
    "Garda Nigeria": ["PAYE NG", "Pension Employee NG", "Pension Employer NG", "NHF NG", "NHIS Employee NG", "NHIS Employer NG", "NSITF NG", "ITF NG"],
    "Garda Angola":  ["PAYE AO", "INSS Employee AO", "INSS Employer AO"],
}

# Invoice amounts per item (multiplier applied per currency)
INVOICE_MULTIPLIERS = {
    "KES": 1,      # base amounts in KES-scale
    "UGX": 30,     # ~30x KES
    "NGN": 10,     # ~10x KES
    "AOA": 6,      # ~6x KES
}

SALES_BASE_AMOUNTS = [500000, 350000, 200000, 750000, 150000]   # KES-equivalent
PURCHASE_BASE_AMOUNTS = [120000, 250000, 80000, 45000, 60000]   # KES-equivalent
```

---

### Task 1: Create the demo module skeleton

**Files:**
- Create: `apps/payroll_africa/payroll_africa/demo/__init__.py`
- Create: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Create directory and __init__.py**

```bash
mkdir -p apps/payroll_africa/payroll_africa/demo
touch apps/payroll_africa/payroll_africa/demo/__init__.py
```

**Step 2: Write the module skeleton with all constants and empty function stubs**

Write `setup_demo_data.py` with:
- All data constants from above
- `execute()` function that calls helpers in order, wrapped in `try/finally` with `frappe.db.commit()`
- `teardown()` function stub
- Helper stubs: `create_items()`, `create_customers()`, `create_suppliers()`, `create_banks()`, `create_employees()`, `create_salary_structures()`, `create_salary_structure_assignments()`, `create_payroll_periods()`, `create_payroll_entries()`, `create_sales_invoices()`, `create_purchase_invoices()`

Each function should print progress (e.g., `print("Creating items...")`).

The `execute()` order:
1. `create_items()`
2. `create_customers()`
3. `create_suppliers()`
4. `create_banks()`
5. `create_employees()`
6. `create_salary_structures()`
7. `create_payroll_periods()`
8. `create_salary_structure_assignments()`
9. `create_payroll_entries()`
10. `create_sales_invoices()`
11. `create_purchase_invoices()`

**Step 3: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/
git commit -m "feat: add demo data module skeleton"
```

---

### Task 2: Implement create_items()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_items()**

```python
def create_items():
    print("Creating service items...")
    for item in ITEMS:
        if frappe.db.exists("Item", item["item_code"]):
            print(f"  Item {item['item_code']} already exists, skipping")
            continue
        doc = frappe.get_doc({
            "doctype": "Item",
            "item_code": item["item_code"],
            "item_name": item["item_name"],
            "item_group": "Services",
            "is_stock_item": 0,
            "include_item_in_manufacturing": 0,
            "description": item["item_name"],
        })
        doc.insert(ignore_permissions=True)
        print(f"  Created {item['item_code']}")
    frappe.db.commit()
```

**Step 2: Test by running**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_items
```

Expected: 5 items created, no errors.

**Step 3: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement create_items for demo data"
```

---

### Task 3: Implement create_customers() and create_suppliers()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_customers()**

```python
def create_customers():
    print("Creating customers...")
    for company, names in CUSTOMERS.items():
        info = COMPANIES[company]
        for name in names:
            if frappe.db.exists("Customer", name):
                print(f"  Customer {name} already exists, skipping")
                continue
            doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": name,
                "customer_group": "Commercial",
                "territory": info["country"],
                "default_currency": info["currency"],
                "companies": [{"company": company}],
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created customer: {name} ({company})")
    frappe.db.commit()
```

Note: If "Commercial" customer group doesn't exist, use whatever default exists. Check with:
```python
frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
```
Fallback to "All Customer Groups" if needed.

**Step 2: Implement create_suppliers()**

```python
def create_suppliers():
    print("Creating suppliers...")
    for company, names in SUPPLIERS.items():
        info = COMPANIES[company]
        for name in names:
            if frappe.db.exists("Supplier", name):
                print(f"  Supplier {name} already exists, skipping")
                continue
            doc = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": name,
                "supplier_group": "Services",
                "country": info["country"],
                "default_currency": info["currency"],
                "companies": [{"company": company}],
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created supplier: {name} ({company})")
    frappe.db.commit()
```

Same note — check that Supplier Group "Services" exists, fallback to default.

**Step 3: Test**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_customers
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_suppliers
```

**Step 4: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement create_customers and create_suppliers"
```

---

### Task 4: Implement create_banks()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_banks()**

For each company:
1. Create `Bank` doctype if not exists (e.g., "Kenya Commercial Bank")
2. Create a GL `Account` under "Bank Accounts - XX" if not exists
3. Create `Bank Account` doctype linking Bank + Company + GL Account

```python
def create_banks():
    print("Creating bank accounts...")
    for company, bank_info in BANKS.items():
        abbr = COMPANIES[company]["abbr"]
        bank_name = bank_info["bank"]
        account_name = bank_info["account_name"]

        # 1. Create Bank doctype
        if not frappe.db.exists("Bank", bank_name):
            frappe.get_doc({"doctype": "Bank", "bank_name": bank_name}).insert(ignore_permissions=True)
            print(f"  Created bank: {bank_name}")

        # 2. Create GL Account under "Bank Accounts - XX"
        gl_account_name = f"{account_name} - {abbr}"
        parent_account = f"Bank Accounts - {abbr}"
        if not frappe.db.exists("Account", gl_account_name):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": account_name,
                "parent_account": parent_account,
                "company": company,
                "account_type": "Bank",
                "is_group": 0,
            }).insert(ignore_permissions=True)
            print(f"  Created GL account: {gl_account_name}")

        # 3. Create Bank Account
        ba_name = f"{account_name} - {company}"
        if not frappe.db.exists("Bank Account", {"bank": bank_name, "company": company}):
            frappe.get_doc({
                "doctype": "Bank Account",
                "account_name": account_name,
                "bank": bank_name,
                "company": company,
                "account": gl_account_name,
                "is_company_account": 1,
                "is_default": 1,
            }).insert(ignore_permissions=True)
            print(f"  Created bank account: {account_name} for {company}")
    frappe.db.commit()
```

**Step 2: Test**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_banks
```

**Step 3: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement create_banks for demo data"
```

---

### Task 5: Implement create_employees()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_employees()**

Creates 5 employees per company, using EMPLOYEE_TEMPLATES for names/details. Each employee gets a unique first_name by appending the country abbreviation (e.g., "James KE", "James UG") to avoid name collisions. Or better, use country-appropriate name prefixes.

```python
# Country-specific employee names
EMPLOYEES = {
    "Garda Kenya": [
        ("James", "Mwangi", "Male", "1980-03-15"),
        ("Grace", "Ochieng", "Female", "1985-07-22"),
        ("Peter", "Kamau", "Male", "1990-01-10"),
        ("Mary", "Wanjiku", "Female", "1992-11-05"),
        ("David", "Oduor", "Male", "1988-06-18"),
    ],
    "Garda Uganda": [
        ("Ronald", "Mugisha", "Male", "1981-04-20"),
        ("Sarah", "Nakamya", "Female", "1986-08-12"),
        ("Joseph", "Ssenyonga", "Male", "1991-02-14"),
        ("Agnes", "Namutebi", "Female", "1993-09-30"),
        ("Henry", "Kato", "Male", "1987-05-25"),
    ],
    "Garda Nigeria": [
        ("Chukwu", "Okafor", "Male", "1982-06-08"),
        ("Amina", "Bello", "Female", "1984-12-01"),
        ("Emeka", "Nwosu", "Male", "1989-03-22"),
        ("Fatima", "Ibrahim", "Female", "1991-10-17"),
        ("Tunde", "Adeyemi", "Male", "1986-01-30"),
    ],
    "Garda Angola": [
        ("Carlos", "da Silva", "Male", "1983-07-14"),
        ("Ana", "Ferreira", "Female", "1987-11-09"),
        ("Miguel", "Santos", "Male", "1990-04-28"),
        ("Luisa", "Neto", "Female", "1992-02-19"),
        ("Paulo", "Domingos", "Male", "1985-08-03"),
    ],
}

DESIGNATIONS = ["Manager", "Consultant", "Associate", "Associate", "Associate"]
DEPARTMENTS = ["Management", "Operations", "Operations", "Operations", "Operations"]

def create_employees():
    print("Creating employees...")
    for company, emp_list in EMPLOYEES.items():
        info = COMPANIES[company]
        abbr = info["abbr"]
        salaries = SALARIES[company]
        for i, (first, last, gender, dob) in enumerate(emp_list):
            full_name = f"{first} {last}"
            # Check if employee already exists by name + company
            exists = frappe.db.exists("Employee", {"employee_name": full_name, "company": company})
            if exists:
                print(f"  Employee {full_name} already exists at {company}, skipping")
                continue

            dept = f"{DEPARTMENTS[i]} - {abbr}"
            doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": first,
                "last_name": last,
                "employee_name": full_name,
                "gender": gender,
                "date_of_birth": dob,
                "date_of_joining": "2025-01-01",
                "company": company,
                "department": dept,
                "designation": DESIGNATIONS[i],
                "status": "Active",
                "payroll_country": info["country"],
                "holiday_list": "",  # will be set if one exists
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created employee: {full_name} ({company})")
    frappe.db.commit()
```

**Important:** If holiday list is mandatory, we may need to create one per company first. Check during execution. If needed, create a simple holiday list "2026 Holidays - XX" with no holidays.

**Step 2: Test**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_employees
```

**Step 3: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement create_employees for demo data"
```

---

### Task 6: Implement create_salary_structures()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_salary_structures()**

Create one salary structure per company. Each has Basic Salary as earning + country deduction components at amount=0 (payroll_africa hook fills in real amounts on salary slip validate).

```python
def create_salary_structures():
    print("Creating salary structures...")
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"

        if frappe.db.exists("Salary Structure", ss_name):
            print(f"  Salary structure {ss_name} already exists, skipping")
            continue

        earnings = [{"salary_component": "Basic Salary", "amount": 0, "formula": "base"}]
        deductions = [
            {"salary_component": comp, "amount": 0}
            for comp in STRUCTURE_DEDUCTIONS[company]
        ]

        doc = frappe.get_doc({
            "doctype": "Salary Structure",
            "name": ss_name,
            "company": company,
            "currency": info["currency"],
            "payroll_frequency": "Monthly",
            "is_active": "Yes",
            "earnings": earnings,
            "deductions": deductions,
        })
        doc.insert(ignore_permissions=True)
        doc.submit()
        print(f"  Created & submitted salary structure: {ss_name}")
    frappe.db.commit()
```

**Note:** Salary Structure must be submitted (docstatus=1) before it can be assigned.

**Step 2: Test**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_salary_structures
```

**Step 3: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement create_salary_structures for demo data"
```

---

### Task 7: Implement create_payroll_periods() and create_salary_structure_assignments()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_payroll_periods()**

```python
def create_payroll_periods():
    print("Creating payroll periods...")
    for company in COMPANIES:
        pp_name = f"FY 2026 - {COMPANIES[company]['abbr']}"
        if frappe.db.exists("Payroll Period", pp_name):
            print(f"  Payroll period {pp_name} already exists, skipping")
            continue
        doc = frappe.get_doc({
            "doctype": "Payroll Period",
            "payroll_period_name": pp_name,
            "company": company,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        })
        doc.insert(ignore_permissions=True)
        print(f"  Created payroll period: {pp_name}")
    frappe.db.commit()
```

**Step 2: Implement create_salary_structure_assignments()**

Assign each employee to their company's salary structure with their specific base salary.

```python
def create_salary_structure_assignments():
    print("Creating salary structure assignments...")
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"
        salaries = SALARIES[company]

        # Get employees for this company
        employees = frappe.get_all(
            "Employee",
            filters={"company": company, "status": "Active"},
            fields=["name", "employee_name"],
            order_by="creation",
        )

        for i, emp in enumerate(employees):
            base = salaries[i] if i < len(salaries) else salaries[-1]

            # Check if assignment already exists
            exists = frappe.db.exists("Salary Structure Assignment", {
                "employee": emp.name,
                "salary_structure": ss_name,
                "docstatus": 1,
            })
            if exists:
                print(f"  SSA for {emp.employee_name} already exists, skipping")
                continue

            doc = frappe.get_doc({
                "doctype": "Salary Structure Assignment",
                "employee": emp.name,
                "salary_structure": ss_name,
                "company": company,
                "currency": info["currency"],
                "from_date": "2026-01-01",
                "base": base,
                "variable": 0,
            })
            doc.insert(ignore_permissions=True)
            doc.submit()
            print(f"  Assigned {emp.employee_name}: {info['currency']} {base:,.0f}")
    frappe.db.commit()
```

**Step 3: Test**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_payroll_periods
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_salary_structure_assignments
```

**Step 4: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement payroll periods and salary structure assignments"
```

---

### Task 8: Implement create_payroll_entries()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_payroll_entries()**

For each company: create a Payroll Entry for January 2026, fill employees, create salary slips, submit them.

```python
def create_payroll_entries():
    print("Creating payroll entries for January 2026...")
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"

        # Check if salary slips already exist for Jan 2026
        existing = frappe.db.count("Salary Slip", {
            "company": company,
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        })
        if existing:
            print(f"  {existing} salary slips already exist for {company} Jan 2026, skipping")
            continue

        doc = frappe.get_doc({
            "doctype": "Payroll Entry",
            "company": company,
            "currency": info["currency"],
            "payroll_frequency": "Monthly",
            "posting_date": "2026-01-31",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "salary_structure": ss_name,
            "cost_center": frappe.db.get_value("Company", company, "cost_center"),
            "payment_account": f"Bank Accounts - {info['abbr']}",
        })
        doc.insert(ignore_permissions=True)
        print(f"  Created payroll entry for {company}")

        # Fill employees
        doc.fill_employee_details()
        doc.save()
        print(f"  Filled {len(doc.employees)} employees")

        # Create salary slips
        doc.create_salary_slips()
        print(f"  Created salary slips for {company}")

        # Submit salary slips
        slips = frappe.get_all("Salary Slip", filters={
            "payroll_entry": doc.name,
            "docstatus": 0,
        }, pluck="name")

        for slip_name in slips:
            slip = frappe.get_doc("Salary Slip", slip_name)
            slip.submit()
            print(f"    Submitted: {slip.employee_name} - Net: {info['currency']} {slip.net_pay:,.0f}")

        # Submit the payroll entry itself
        doc.reload()
        doc.submit()
        print(f"  Submitted payroll entry: {doc.name}")

    frappe.db.commit()
```

**Step 2: Test**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_payroll_entries
```

This is the critical test — verifies that the payroll_africa hook auto-calculates statutory deductions.

**Step 3: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement create_payroll_entries with salary slip submission"
```

---

### Task 9: Implement create_sales_invoices() and create_purchase_invoices()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement create_sales_invoices()**

```python
def create_sales_invoices():
    print("Creating sales invoices...")
    for company in COMPANIES:
        info = COMPANIES[company]
        customers = CUSTOMERS[company]
        multiplier = INVOICE_MULTIPLIERS[info["currency"]]

        for i, customer_name in enumerate(customers):
            item = ITEMS[i]
            amount = SALES_BASE_AMOUNTS[i] * multiplier

            # Check if already exists
            exists = frappe.db.exists("Sales Invoice", {
                "customer": customer_name,
                "company": company,
                "posting_date": "2026-01-15",
                "docstatus": 1,
            })
            if exists:
                print(f"  Sales invoice for {customer_name} already exists, skipping")
                continue

            doc = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": customer_name,
                "company": company,
                "currency": info["currency"],
                "posting_date": "2026-01-15",
                "due_date": "2026-02-15",
                "debit_to": f"Debtors - {info['abbr']}",
                "items": [{
                    "item_code": item["item_code"],
                    "qty": 1,
                    "rate": amount,
                    "income_account": f"Service - {info['abbr']}",
                    "cost_center": frappe.db.get_value("Company", company, "cost_center"),
                }],
            })
            doc.insert(ignore_permissions=True)
            doc.submit()
            print(f"  Created SI: {customer_name} - {info['currency']} {amount:,.0f}")
    frappe.db.commit()
```

**Step 2: Implement create_purchase_invoices()**

```python
def create_purchase_invoices():
    print("Creating purchase invoices...")
    for company in COMPANIES:
        info = COMPANIES[company]
        suppliers = SUPPLIERS[company]
        multiplier = INVOICE_MULTIPLIERS[info["currency"]]

        for i, supplier_name in enumerate(suppliers):
            item = ITEMS[i]
            amount = PURCHASE_BASE_AMOUNTS[i] * multiplier

            exists = frappe.db.exists("Purchase Invoice", {
                "supplier": supplier_name,
                "company": company,
                "posting_date": "2026-01-20",
                "docstatus": 1,
            })
            if exists:
                print(f"  Purchase invoice for {supplier_name} already exists, skipping")
                continue

            doc = frappe.get_doc({
                "doctype": "Purchase Invoice",
                "supplier": supplier_name,
                "company": company,
                "currency": info["currency"],
                "posting_date": "2026-01-20",
                "due_date": "2026-02-20",
                "credit_to": f"Creditors - {info['abbr']}",
                "items": [{
                    "item_code": item["item_code"],
                    "qty": 1,
                    "rate": amount,
                    "expense_account": f"Cost of Goods Sold - {info['abbr']}",
                    "cost_center": frappe.db.get_value("Company", company, "cost_center"),
                }],
            })
            doc.insert(ignore_permissions=True)
            doc.submit()
            print(f"  Created PI: {supplier_name} - {info['currency']} {amount:,.0f}")
    frappe.db.commit()
```

**Step 3: Test**

```bash
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_sales_invoices
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.create_purchase_invoices
```

**Step 4: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: implement sales and purchase invoice creation"
```

---

### Task 10: Implement teardown() and wire up execute()

**Files:**
- Modify: `apps/payroll_africa/payroll_africa/demo/setup_demo_data.py`

**Step 1: Implement teardown()**

Deletes all demo data in reverse dependency order. Must cancel submitted docs first.

```python
def teardown():
    """Remove all demo data. Run: bench --site gardaworld execute payroll_africa.demo.setup_demo_data.teardown"""
    print("Tearing down demo data...")
    frappe.flags.ignore_permissions = True

    # 1. Cancel + delete payroll entries and salary slips
    for company in COMPANIES:
        # Cancel salary slips first
        slips = frappe.get_all("Salary Slip", filters={"company": company, "docstatus": 1}, pluck="name")
        for s in slips:
            frappe.get_doc("Salary Slip", s).cancel()
        frappe.db.delete("Salary Slip", {"company": company})

        # Cancel + delete payroll entries
        entries = frappe.get_all("Payroll Entry", filters={"company": company, "docstatus": 1}, pluck="name")
        for e in entries:
            frappe.get_doc("Payroll Entry", e).cancel()
        frappe.db.delete("Payroll Entry", {"company": company})
        print(f"  Cleaned payroll for {company}")

    # 2. Cancel + delete invoices
    for company in COMPANIES:
        for dt in ["Sales Invoice", "Purchase Invoice"]:
            docs = frappe.get_all(dt, filters={"company": company, "docstatus": 1}, pluck="name")
            for d in docs:
                frappe.get_doc(dt, d).cancel()
            frappe.db.delete(dt, {"company": company})
        print(f"  Cleaned invoices for {company}")

    # 3. Delete salary structure assignments (cancel first)
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"
        ssas = frappe.get_all("Salary Structure Assignment", filters={"salary_structure": ss_name, "docstatus": 1}, pluck="name")
        for s in ssas:
            frappe.get_doc("Salary Structure Assignment", s).cancel()
        frappe.db.delete("Salary Structure Assignment", {"salary_structure": ss_name})

    # 4. Cancel + delete salary structures
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"
        if frappe.db.exists("Salary Structure", ss_name):
            doc = frappe.get_doc("Salary Structure", ss_name)
            if doc.docstatus == 1:
                doc.cancel()
            doc.delete()
            print(f"  Deleted salary structure: {ss_name}")

    # 5. Delete payroll periods
    for company in COMPANIES:
        pp_name = f"FY 2026 - {COMPANIES[company]['abbr']}"
        if frappe.db.exists("Payroll Period", pp_name):
            frappe.delete_doc("Payroll Period", pp_name, force=True)

    # 6. Delete employees
    for company, emp_list in EMPLOYEES.items():
        for first, last, _, _ in emp_list:
            full_name = f"{first} {last}"
            emps = frappe.get_all("Employee", filters={"employee_name": full_name, "company": company}, pluck="name")
            for e in emps:
                frappe.delete_doc("Employee", e, force=True)
        print(f"  Deleted employees for {company}")

    # 7. Delete bank accounts, GL accounts, banks
    for company, bank_info in BANKS.items():
        abbr = COMPANIES[company]["abbr"]
        ba = frappe.get_all("Bank Account", filters={"bank": bank_info["bank"], "company": company}, pluck="name")
        for b in ba:
            frappe.delete_doc("Bank Account", b, force=True)
        gl = f"{bank_info['account_name']} - {abbr}"
        if frappe.db.exists("Account", gl):
            frappe.delete_doc("Account", gl, force=True)
        if frappe.db.exists("Bank", bank_info["bank"]):
            # Only delete if no other bank accounts reference it
            remaining = frappe.db.count("Bank Account", {"bank": bank_info["bank"]})
            if not remaining:
                frappe.delete_doc("Bank", bank_info["bank"], force=True)

    # 8. Delete customers
    for company, names in CUSTOMERS.items():
        for name in names:
            if frappe.db.exists("Customer", name):
                frappe.delete_doc("Customer", name, force=True)

    # 9. Delete suppliers
    for company, names in SUPPLIERS.items():
        for name in names:
            if frappe.db.exists("Supplier", name):
                frappe.delete_doc("Supplier", name, force=True)

    # 10. Delete items
    for item in ITEMS:
        if frappe.db.exists("Item", item["item_code"]):
            frappe.delete_doc("Item", item["item_code"], force=True)

    frappe.db.commit()
    frappe.flags.ignore_permissions = False
    print("Teardown complete!")
```

**Step 2: Wire up execute()**

```python
def execute():
    """Create all demo data. Run: bench --site gardaworld execute payroll_africa.demo.setup_demo_data.execute"""
    print("=" * 60)
    print("Setting up Payroll Africa demo data...")
    print("=" * 60)

    create_items()
    create_customers()
    create_suppliers()
    create_banks()
    create_employees()
    create_salary_structures()
    create_payroll_periods()
    create_salary_structure_assignments()
    create_payroll_entries()
    create_sales_invoices()
    create_purchase_invoices()

    print("=" * 60)
    print("Demo data setup complete!")
    print("=" * 60)
```

**Step 3: Full integration test**

```bash
# First teardown any partial data
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.teardown
# Then create everything
bench --site gardaworld execute payroll_africa.demo.setup_demo_data.execute
```

Expected output: all 20 customers, 20 suppliers, 4 banks, 20 employees, 4 salary structures, 20 salary slips with auto-calculated deductions, 20 sales invoices, 20 purchase invoices.

**Step 4: Commit**

```bash
git add apps/payroll_africa/payroll_africa/demo/setup_demo_data.py
git commit -m "feat: complete demo data script with execute and teardown"
```

---

### Task 11: Verify and validate

**Step 1: Check salary slips have correct deductions**

```bash
bench --site gardaworld execute frappe.get_all --args '["Salary Slip"]' --kwargs '{"fields":["employee_name","company","gross_pay","total_deduction","net_pay"],"filters":{"docstatus":1},"limit_page_length":25}'
```

Verify each country has 5 slips with nonzero deductions.

**Step 2: Check invoices**

```bash
bench --site gardaworld execute frappe.get_all --args '["Sales Invoice"]' --kwargs '{"fields":["customer","company","grand_total","status"],"filters":{"docstatus":1},"limit_page_length":25}'
bench --site gardaworld execute frappe.get_all --args '["Purchase Invoice"]' --kwargs '{"fields":["supplier","company","grand_total","status"],"filters":{"docstatus":1},"limit_page_length":25}'
```

**Step 3: Test the new Africa Standard print format on a salary slip**

Open a salary slip in browser and select "Salary Slip Africa Standard" print format to verify it renders correctly.

**Step 4: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix: adjustments from demo data validation"
```
