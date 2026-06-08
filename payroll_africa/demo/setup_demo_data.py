import frappe
from frappe.utils import flt

COMPANIES = {
    "Garda Kenya":      {"abbr": "GK",  "currency": "KES", "country": "Kenya"},
    "Garda Uganda":     {"abbr": "GU",  "currency": "UGX", "country": "Uganda"},
    "Garda Nigeria":    {"abbr": "GN",  "currency": "NGN", "country": "Nigeria"},
    "Garda Angola":     {"abbr": "GA",  "currency": "AOA", "country": "Angola"},
    "Garda Tanzania":   {"abbr": "GT",  "currency": "TZS", "country": "Tanzania"},
    "GARDA RWANDA":     {"abbr": "GR",  "currency": "RWF", "country": "Rwanda"},
    "Garda Zambia":     {"abbr": "GZ",  "currency": "ZMW", "country": "Zambia"},
    "Garda Mozambique": {"abbr": "GMZ", "currency": "MZN", "country": "Mozambique"},
    "Garda Malawi":     {"abbr": "GM",  "currency": "MWK", "country": "Malawi"},
    "Garda DRC":        {"abbr": "GD",  "currency": "CDF", "country": "Congo, The Democratic Republic of the"},
    "Garda Burundi":    {"abbr": "GB",  "currency": "BIF", "country": "Burundi"},
    "Garda Ethiopia":      {"abbr": "GET", "currency": "ETB", "country": "Ethiopia"},
    "Garda Botswana":      {"abbr": "GBW", "currency": "BWP", "country": "Botswana"},
    "Garda Ghana":         {"abbr": "GHG", "currency": "GHS", "country": "Ghana"},
    "Garda South Africa":  {"abbr": "GZA", "currency": "ZAR", "country": "South Africa"},
    "Garda Egypt":         {"abbr": "GEG", "currency": "EGP", "country": "Egypt"},
    "Garda Morocco":       {"abbr": "GMA", "currency": "MAD", "country": "Morocco"},
    "Garda Ivory Coast":   {"abbr": "GCI", "currency": "XOF", "country": "Ivory Coast"},
    "Garda Tunisia":       {"abbr": "GTN", "currency": "TND", "country": "Tunisia"},
    "Garda Namibia":       {"abbr": "GNA", "currency": "NAD", "country": "Namibia"},
    "Garda Madagascar":    {"abbr": "GMG", "currency": "MGA", "country": "Madagascar"},
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
    "Garda Tanzania":   ["Vodacom Tanzania", "CRDB Bank", "Tanzania Breweries", "Airtel Tanzania", "NMB Bank TZ"],
    "GARDA RWANDA":     ["MTN Rwanda", "Bank of Kigali", "Bralirwa", "Airtel Rwanda", "I&M Bank Rwanda"],
    "Garda Zambia":     ["Zambia Sugar", "Zanaco Bank", "Airtel Zambia", "Zambeef Products", "Stanbic Zambia"],
    "Garda Mozambique": ["Mozal Aluminium", "BCI Mozambique", "Cervejas de Mocambique", "Vodacom Mozambique", "TDM Telecomunicacoes"],
    "Garda Malawi":     ["Illovo Sugar Malawi", "National Bank of Malawi", "Airtel Malawi", "Press Corporation", "FDH Bank Malawi"],
    "Garda DRC":        ["Rawbank DRC", "Vodacom Congo", "Brasimba SARL", "Orange RDC", "Equity BCDC"],
    "Garda Burundi":    ["Brarudi SA", "Econet Leo Burundi", "Interbank Burundi", "SOSUMO Burundi", "KCB Burundi"],
    "Garda Ethiopia":      ["Ethiopian Airlines", "CBE Ethiopia", "Safaricom Ethiopia", "Ethio Telecom", "Dashen Bank"],
    "Garda Botswana":      ["Debswana Diamond", "BPC Botswana", "Mascom Botswana", "Letshego Holdings", "Stanbic Botswana"],
    "Garda Ghana":         ["MTN Ghana", "GCB Bank", "Ghana National Petroleum", "AirtelTigo Ghana", "Ecobank Ghana"],
    "Garda South Africa":  ["MTN South Africa", "Standard Bank SA", "Sasol", "Pick n Pay", "Absa Bank"],
    "Garda Egypt":         ["EgyptAir", "QNB Egypt", "Telecom Egypt", "CIB Egypt", "EFG Hermes"],
    "Garda Morocco":       ["Maroc Telecom", "Attijariwafa Bank", "OCP Group", "BMCE Bank", "Royal Air Maroc"],
    "Garda Ivory Coast":   ["Orange CI", "NSIA Banque", "SOTRA CI", "CMA CGM CI", "Bank of Africa CI"],
    "Garda Tunisia":       ["Ooredoo Tunisia", "Attijari Bank Tunisia", "Tunisie Telecom", "BIAT Tunisia", "Tunisair"],
    "Garda Namibia":       ["MTC Namibia", "Bank Windhoek", "NamPower", "FirstRand Namibia", "Namibia Breweries"],
    "Garda Madagascar":    ["Telma Madagascar", "BFV-Societe Generale", "Air Madagascar", "BMOI Madagascar", "Jirama"],
}

SUPPLIERS = {
    "Garda Kenya":   ["Safeguard Supplies KE", "Nairobi Fleet Leasing", "Telkom Kenya", "KK Security Supplies", "Nelly's Cleaning KE"],
    "Garda Uganda":  ["Kampala Uniforms", "Entebbe Transport", "Airtel Uganda Biz", "Pearl Uniforms UG", "Cleantek Uganda"],
    "Garda Nigeria": ["Abuja Security Equip", "Lagos Vehicle Hire", "MTN Nigeria Biz", "Hallmark Security NG", "CleanServ Nigeria"],
    "Garda Angola":  ["Luanda Tactical", "Sonangol Fuel", "Movicel Business", "Segurança Supplies", "Limpeza Angola"],
    "Garda Tanzania":   ["Dar Uniforms TZ", "Safari Fleet TZ", "Halotel Business", "SecureKit Tanzania", "CleanPro Tanzania"],
    "GARDA RWANDA":     ["Kigali Uniforms", "RwandAir Fleet", "MTN Rwanda Biz", "SafeGuard Rwanda", "CleanServ Rwanda"],
    "Garda Zambia":     ["Lusaka Security Supplies", "Zambia Fleet Hire", "MTN Zambia Biz", "GuardTech Zambia", "CleanZam Services"],
    "Garda Mozambique": ["Maputo Tactical", "Mocambique Fleet", "Tmcel Business", "Seguranca Maputo", "Limpeza Mocambique"],
    "Garda Malawi":     ["Lilongwe Supplies", "Malawi Fleet Services", "TNM Business MW", "GuardForce Malawi", "CleanTech Malawi"],
    "Garda DRC":        ["Kinshasa Security Equip", "Congo Fleet Hire", "Vodacom Congo Biz", "Securite Kinshasa", "Proprete Congo"],
    "Garda Burundi":    ["Bujumbura Supplies", "Burundi Fleet Lease", "Lumitel Business", "SecureForce Burundi", "NettService Burundi"],
    "Garda Ethiopia":      ["Addis Security Equip", "Ethiopia Fleet Hire", "Safaricom Ethiopia Biz", "SegurTech Ethiopia", "CleanPro Ethiopia"],
    "Garda Botswana":      ["Gaborone Supplies", "Botswana Fleet Services", "Mascom Business BW", "GuardTech Botswana", "CleanZam BW"],
    "Garda Ghana":         ["Accra Security Equip", "Ghana Fleet Hire", "MTN Ghana Biz", "SafeGuard Ghana", "CleanServ Ghana"],
    "Garda South Africa":  ["JHB Tactical", "SA Fleet Hire", "Vodacom SA Biz", "SecureGuard SA", "CleanPro SA"],
    "Garda Egypt":         ["Cairo Security Equip", "Egypt Fleet Lease", "Vodafone Egypt Biz", "SecurTech Egypt", "CleanServ Egypt"],
    "Garda Morocco":       ["Casablanca Supplies", "Morocco Fleet Hire", "Inwi Business", "Seguranca Morocco", "Limpeza Morocco"],
    "Garda Ivory Coast":   ["Abidjan Supplies", "CI Fleet Services", "Orange CI Biz", "SecureForce CI", "NettService CI"],
    "Garda Tunisia":       ["Tunis Security Equip", "Tunisia Fleet Lease", "Ooredoo Biz TN", "SafeGuard Tunisia", "CleanPro Tunisia"],
    "Garda Namibia":       ["Windhoek Supplies", "Namibia Fleet Hire", "MTC Namibia Biz", "GuardTech Namibia", "CleanNam Services"],
    "Garda Madagascar":    ["Antananarivo Supplies", "Madagascar Fleet", "Telma Business MG", "SecureForce MG", "NettService MG"],
}

BANKS = {
    "Garda Kenya":   {"bank": "Kenya Commercial Bank",       "account_name": "KCB Main Account"},
    "Garda Uganda":  {"bank": "Standard Chartered Uganda",   "account_name": "StanChart Main Account"},
    "Garda Nigeria": {"bank": "First Bank Nigeria",          "account_name": "FirstBank Main Account"},
    "Garda Angola":  {"bank": "Banco BAI",                   "account_name": "BAI Main Account"},
    "Garda Tanzania":   {"bank": "CRDB Bank Tanzania",    "account_name": "CRDB Main Account"},
    "GARDA RWANDA":     {"bank": "Bank of Kigali",        "account_name": "BK Main Account"},
    "Garda Zambia":     {"bank": "Zanaco Bank",           "account_name": "Zanaco Main Account"},
    "Garda Mozambique": {"bank": "BCI Mozambique",        "account_name": "BCI Main Account"},
    "Garda Malawi":     {"bank": "National Bank Malawi",  "account_name": "NBM Main Account"},
    "Garda DRC":        {"bank": "Rawbank",               "account_name": "Rawbank Main Account"},
    "Garda Burundi":    {"bank": "Interbank Burundi",     "account_name": "Interbank Main Account"},
    "Garda Ethiopia":      {"bank": "Commercial Bank of Ethiopia", "account_name": "CBE Main Account"},
    "Garda Botswana":      {"bank": "Stanbic Bank Botswana",       "account_name": "Stanbic BW Main Account"},
    "Garda Ghana":         {"bank": "Ghana Commercial Bank",       "account_name": "GCB Main Account"},
    "Garda South Africa":  {"bank": "Standard Bank South Africa",  "account_name": "Standard Bank SA Main Account"},
    "Garda Egypt":         {"bank": "QNB Egypt",                   "account_name": "QNB Main Account"},
    "Garda Morocco":       {"bank": "Attijariwafa Bank",           "account_name": "Attijariwafa Main Account"},
    "Garda Ivory Coast":   {"bank": "NSIA Banque",                 "account_name": "NSIA Main Account"},
    "Garda Tunisia":       {"bank": "Attijari Bank Tunisia",       "account_name": "Attijari TN Main Account"},
    "Garda Namibia":       {"bank": "Bank Windhoek",               "account_name": "Bank Windhoek Main Account"},
    "Garda Madagascar":    {"bank": "BFV-Societe Generale",        "account_name": "BFV Main Account"},
}

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
    "Garda Ethiopia": [
        ("Dawit", "Abebe", "Male", "1982-03-15"),
        ("Hanna", "Tadesse", "Female", "1986-07-22"),
        ("Solomon", "Kebede", "Male", "1990-01-10"),
        ("Meron", "Bekele", "Female", "1992-11-05"),
        ("Yonas", "Hailu", "Male", "1988-06-18"),
    ],
    "Garda Botswana": [
        ("Kabelo", "Mokgwathi", "Male", "1981-04-20"),
        ("Lesego", "Kgosi", "Female", "1985-08-12"),
        ("Thuso", "Mokgosi", "Male", "1991-02-14"),
        ("Amantle", "Montsho", "Female", "1993-09-30"),
        ("Tumelo", "Kgafela", "Male", "1987-05-25"),
    ],
    "Garda Ghana": [
        ("Kwame", "Asante", "Male", "1982-06-08"),
        ("Akosua", "Mensah", "Female", "1984-12-01"),
        ("Kofi", "Boateng", "Male", "1989-03-22"),
        ("Abena", "Owusu", "Female", "1991-10-17"),
        ("Yaw", "Addo", "Male", "1986-01-30"),
    ],
    "Garda South Africa": [
        ("Siyabonga", "Nkabinde", "Male", "1983-07-14"),
        ("Lerato", "Mokoena", "Female", "1987-11-09"),
        ("Thabo", "Dlamini", "Male", "1990-04-28"),
        ("Nomsa", "Zulu", "Female", "1992-02-19"),
        ("Bongani", "Mbatha", "Male", "1985-08-03"),
    ],
    "Garda Egypt": [
        ("Omar", "Hassan", "Male", "1982-05-10"),
        ("Fatima", "Ibrahim", "Female", "1986-09-14"),
        ("Amr", "Mahmoud", "Male", "1990-03-28"),
        ("Nour", "Sayed", "Female", "1991-12-02"),
        ("Karim", "Fouad", "Male", "1987-07-19"),
    ],
    "Garda Morocco": [
        ("Youssef", "El Amrani", "Male", "1983-02-25"),
        ("Amina", "Bennani", "Female", "1987-06-11"),
        ("Mehdi", "Fassi", "Male", "1989-10-05"),
        ("Salma", "Idrissi", "Female", "1992-04-17"),
        ("Hicham", "Ouazzani", "Male", "1986-08-30"),
    ],
    "Garda Ivory Coast": [
        ("Kouame", "Kone", "Male", "1981-11-08"),
        ("Aya", "Yao", "Female", "1985-04-22"),
        ("Yao", "Kouassi", "Male", "1990-07-15"),
        ("Mariam", "Bamba", "Female", "1993-01-28"),
        ("Jean", "Amani", "Male", "1988-09-12"),
    ],
    "Garda Tunisia": [
        ("Ahmed", "Ben Ali", "Male", "1982-08-20"),
        ("Sana", "Trabelsi", "Female", "1986-12-05"),
        ("Mehdi", "Guesmi", "Male", "1991-02-18"),
        ("Rania", "Jaziri", "Female", "1992-06-30"),
        ("Hatem", "Bouazizi", "Male", "1985-10-14"),
    ],
    "Garda Namibia": [
        ("Johannes", "Nambala", "Male", "1983-04-12"),
        ("Maria", "Shikongo", "Female", "1987-08-25"),
        ("Petrus", "Iiyambo", "Male", "1990-11-07"),
        ("Helena", "Nuuyoma", "Female", "1992-03-19"),
        ("Tobias", "Hainyeko", "Male", "1986-06-01"),
    ],
    "Garda Madagascar": [
        ("Andry", "Rajoelina", "Male", "1982-01-15"),
        ("Mialy", "Rakoto", "Female", "1986-05-28"),
        ("Hery", "Rajaonarimampianina", "Male", "1989-09-10"),
        ("Lalao", "Ravalomanana", "Female", "1991-07-22"),
        ("Rivo", "Andrianarivo", "Male", "1987-12-04"),
    ],
}

DESIGNATIONS = ["Manager", "Consultant", "Associate", "Associate", "Associate"]
DEPARTMENTS = ["Management", "Operations", "Operations", "Operations", "Operations"]

SALARIES = {
    "Garda Kenya":   [150000, 120000, 80000, 60000, 50000],
    "Garda Uganda":  [4000000, 3000000, 2000000, 1800000, 1500000],
    "Garda Nigeria": [900000, 700000, 500000, 350000, 300000],
    "Garda Angola":  [500000, 400000, 280000, 200000, 150000],
    "Garda Tanzania":   [1200000, 950000, 650000, 500000, 400000],
    "GARDA RWANDA":     [800000, 600000, 400000, 300000, 250000],
    "Garda Zambia":     [25000, 20000, 14000, 10000, 8000],
    "Garda Mozambique": [120000, 95000, 65000, 50000, 40000],
    "Garda Malawi":     [800000, 600000, 400000, 300000, 250000],
    "Garda DRC":        [2500000, 2000000, 1400000, 1000000, 800000],
    "Garda Burundi":    [1500000, 1200000, 800000, 600000, 500000],
    "Garda Ethiopia":      [45000, 35000, 25000, 18000, 15000],
    "Garda Botswana":      [25000, 20000, 14000, 10000, 8000],
    "Garda Ghana":         [12000, 9500, 6500, 5000, 4000],
    "Garda South Africa":  [45000, 35000, 25000, 18000, 15000],
    "Garda Egypt":         [25000, 20000, 14000, 10000, 8000],
    "Garda Morocco":       [15000, 12000, 8000, 6000, 5000],
    "Garda Ivory Coast":   [800000, 600000, 400000, 300000, 250000],
    "Garda Tunisia":       [4500, 3500, 2500, 1800, 1500],
    "Garda Namibia":       [25000, 20000, 14000, 10000, 8000],
    "Garda Madagascar":    [4500000, 3500000, 2500000, 1800000, 1500000],
}

STRUCTURE_DEDUCTIONS = {
    "Garda Kenya":   ["PAYE", "NSSF Employee", "NSSF Employer", "SHIF", "Housing Levy", "Employer Housing Levy", "NITA"],
    "Garda Uganda":  ["PAYE UG", "NSSF Employee UG", "NSSF Employer UG", "LST"],
    "Garda Nigeria": ["PAYE NG", "Pension Employee NG", "Pension Employer NG", "NHF NG", "NHIS Employee NG", "NHIS Employer NG", "NSITF NG", "ITF NG"],
    "Garda Angola":  ["PAYE AO", "INSS Employee AO", "INSS Employer AO"],
    "Garda Tanzania":   ["PAYE TZ", "NSSF Employee TZ", "NSSF Employer TZ", "SDL", "WCF"],
    "GARDA RWANDA":     ["PAYE RW", "Pension Employee RW", "Pension Employer RW", "Maternity Employee RW", "Maternity Employer RW", "CBHI RW", "Occupational Hazards RW"],
    "Garda Zambia":     ["PAYE ZM", "NAPSA Employee ZM", "NAPSA Employer ZM", "NHIMA Employee ZM", "NHIMA Employer ZM"],
    "Garda Mozambique": ["PAYE MZ", "INSS Employee MZ", "INSS Employer MZ"],
    "Garda Malawi":     ["PAYE MW", "Pension Employee MW", "Pension Employer MW"],
    "Garda DRC":        ["PAYE CD", "INSS Pension Employee CD", "INSS Pension Employer CD", "INSS Family Benefits CD", "INSS Occupational Risks CD", "INPP CD", "ONEM CD"],
    "Garda Burundi":    ["PAYE BI", "INSS Employee BI", "INSS Employer BI", "Health Insurance Employee BI", "Health Insurance Employer BI", "Training Fund Employee BI", "Training Fund Employer BI", "Work Injury BI"],
    "Garda Ethiopia":      ["PAYE ET", "Pension Employee ET", "Pension Employer ET", "Social Insurance Employee ET", "Social Insurance Employer ET"],
    "Garda Botswana":      ["PAYE BW", "BPOPF Employee BW", "BPOPF Employer BW", "BOMPEC Employee BW", "BOMPEC Employer BW"],
    "Garda Ghana":         ["PAYE GH", "SSNIT Employee GH", "SSNIT Employer GH", "NHIL GH", "GETFund GH"],
    "Garda South Africa":  ["PAYE ZA", "UIF Employee ZA", "UIF Employer ZA", "SDL ZA", "Pension Employee ZA", "Pension Employer ZA"],
    "Garda Egypt":         ["PAYE EG", "Social Insurance Employee EG", "Social Insurance Employer EG", "Health Insurance Employee EG", "Health Insurance Employer EG"],
    "Garda Morocco":       ["PAYE MA", "CNSS Employee MA", "CNSS Employer MA", "AMO Employee MA", "AMO Employer MA"],
    "Garda Ivory Coast":   ["PAYE CI", "CNPS Employee CI", "CNPS Employer CI", "AMU Employee CI", "AMU Employer CI"],
    "Garda Tunisia":       ["PAYE TN", "CNSS Employee TN", "CNSS Employer TN", "CNAM Employee TN", "CNAM Employer TN"],
    "Garda Namibia":       ["PAYE NA", "Social Security Employee NA", "Social Security Employer NA", "NEC NA"],
    "Garda Madagascar":    ["PAYE MG", "CNAPS Employee MG", "CNAPS Employer MG", "OSIE Employee MG", "OSIE Employer MG"],
}

TAX_SLABS = {
    "Garda Kenya":   "Kenya PAYE 2025",
    "Garda Uganda":  "Uganda PAYE 2025",
    "Garda Nigeria": "Nigeria PAYE 2025",
    "Garda Angola":  "Angola PAYE 2025",
    "Garda Tanzania":   "Tanzania PAYE 2025",
    "GARDA RWANDA":     "Rwanda PAYE 2025",
    "Garda Zambia":     "Zambia PAYE 2025",
    "Garda Mozambique": "Mozambique PAYE 2025",
    "Garda Malawi":     "Malawi PAYE 2025",
    "Garda DRC":        "DRC PAYE 2025",
    "Garda Burundi":    "Burundi PAYE 2025",
    "Garda Ethiopia":      "Ethiopia PAYE 2025",
    "Garda Botswana":      "Botswana PAYE 2025",
    "Garda Ghana":         "Ghana PAYE 2025",
    "Garda South Africa":  "South Africa PAYE 2025",
    "Garda Egypt":         "Egypt PAYE 2025",
    "Garda Morocco":       "Morocco PAYE 2025",
    "Garda Ivory Coast":   "Ivory Coast PAYE 2025",
    "Garda Tunisia":       "Tunisia PAYE 2025",
    "Garda Namibia":       "Namibia PAYE 2025",
    "Garda Madagascar":    "Madagascar PAYE 2025",
}

INVOICE_MULTIPLIERS = {
    "KES": 1,
    "UGX": 30,
    "NGN": 10,
    "AOA": 6,
    "TZS": 20,
    "RWF": 8,
    "ZMW": 0.2,
    "MZN": 0.5,
    "MWK": 12,
    "CDF": 20,
    "BIF": 20,
    "ETB": 55,
    "BWP": 0.15,
    "GHS": 0.8,
    "ZAR": 0.2,
    "EGP": 0.5,
    "MAD": 0.1,
    "XOF": 6,
    "TND": 0.3,
    "NAD": 0.15,
    "MGA": 450,
}

SALES_BASE_AMOUNTS = [500000, 350000, 200000, 750000, 150000]
PURCHASE_BASE_AMOUNTS = [120000, 250000, 80000, 45000, 60000]


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


def _ensure_territory(country):
    """Create territory for country if it doesn't exist."""
    if not frappe.db.exists("Territory", country):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": country,
            "parent_territory": "All Territories",
        }).insert(ignore_permissions=True)
        print(f"  Created territory: {country}")


def create_customers():
    print("Creating customers...")
    for company, names in CUSTOMERS.items():
        info = COMPANIES[company]
        _ensure_territory(info["country"])
        for name in names:
            if frappe.db.exists("Customer", name):
                print(f"  Customer {name} already exists, skipping")
                continue
            doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": name,
                "customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups",
                "territory": info["country"],
                "default_currency": info["currency"],
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created customer: {name} ({company})")
    frappe.db.commit()


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
                "supplier_group": frappe.db.get_single_value("Buying Settings", "supplier_group") or "All Supplier Groups",
                "country": info["country"],
                "default_currency": info["currency"],
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created supplier: {name} ({company})")
    frappe.db.commit()


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
        #    For child companies, create in root company first (auto-syncs down)
        gl_account_name = f"{account_name} - {abbr}"
        parent_account = f"Bank Accounts - {abbr}"
        if not frappe.db.exists("Account", gl_account_name):
            root_company = frappe.db.get_value("Company", company, "parent_company")
            if root_company:
                root_abbr = frappe.db.get_value("Company", root_company, "abbr")
                root_gl = f"{account_name} - {root_abbr}"
                root_parent = f"Bank Accounts - {root_abbr}"
                if not frappe.db.exists("Account", root_gl):
                    frappe.get_doc({
                        "doctype": "Account",
                        "account_name": account_name,
                        "parent_account": root_parent,
                        "company": root_company,
                        "account_type": "Bank",
                        "is_group": 0,
                    }).insert(ignore_permissions=True)
                    print(f"  Created root GL account: {root_gl}")
            else:
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


def _ensure_holiday_list(company, abbr):
    """Create a basic holiday list for 2026 and assign it via Holiday List Assignment."""
    hl_name = f"2026 Holidays - {abbr}"
    if not frappe.db.exists("Holiday List", hl_name):
        hl = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": hl_name,
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "country": COMPANIES[company]["country"],
        })
        hl.insert(ignore_permissions=True)
        print(f"  Created holiday list: {hl_name}")

    # HRMS uses Holiday List Assignment (submitted) to resolve holiday lists
    existing_hla = frappe.db.exists("Holiday List Assignment", {
        "assigned_to": company,
        "holiday_list": hl_name,
        "docstatus": 1,
    })
    if not existing_hla:
        hla = frappe.get_doc({
            "doctype": "Holiday List Assignment",
            "applicable_for": "Company",
            "assigned_to": company,
            "holiday_list": hl_name,
            "from_date": "2026-01-01",
        })
        hla.insert(ignore_permissions=True)
        hla.submit()
        print(f"  Created holiday list assignment for {company}")


def create_employees():
    print("Creating employees...")
    for company, emp_list in EMPLOYEES.items():
        info = COMPANIES[company]
        abbr = info["abbr"]
        _ensure_holiday_list(company, abbr)
        for i, (first, last, gender, dob) in enumerate(emp_list):
            full_name = f"{first} {last}"
            exists = frappe.db.exists("Employee", {"employee_name": full_name, "company": company})
            if exists:
                print(f"  Employee {full_name} already exists at {company}, skipping")
                continue

            dept = f"{DEPARTMENTS[i]} - {abbr}"
            doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": first,
                "last_name": last,
                "gender": gender,
                "date_of_birth": dob,
                "date_of_joining": "2025-01-01",
                "company": company,
                "department": dept,
                "designation": DESIGNATIONS[i],
                "status": "Active",
                "payroll_country": info["country"],
            })
            doc.insert(ignore_permissions=True)
            print(f"  Created employee: {full_name} ({company})")
    frappe.db.commit()


def create_salary_structures():
    print("Creating salary structures...")
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"

        if frappe.db.exists("Salary Structure", ss_name):
            print(f"  Salary structure {ss_name} already exists, skipping")
            continue

        earnings = [{"salary_component": "Basic Salary", "amount": 0, "formula": "base", "amount_based_on_formula": 1}]
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


def create_payroll_periods():
    print("Creating payroll periods...")
    for company in COMPANIES:
        pp_name = f"FY 2026 - {COMPANIES[company]['abbr']}"
        if frappe.db.exists("Payroll Period", pp_name):
            print(f"  Payroll period {pp_name} already exists, skipping")
            continue
        doc = frappe.get_doc({
            "doctype": "Payroll Period",
            "name": pp_name,
            "payroll_period_name": pp_name,
            "company": company,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        })
        doc.insert(ignore_permissions=True, set_name=pp_name)
        print(f"  Created payroll period: {pp_name}")
    frappe.db.commit()


def create_salary_structure_assignments():
    print("Creating salary structure assignments...")
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"
        salaries = SALARIES[company]

        employees = frappe.get_all(
            "Employee",
            filters={"company": company, "status": "Active"},
            fields=["name", "employee_name"],
            order_by="creation",
        )

        for i, emp in enumerate(employees):
            base = salaries[i] if i < len(salaries) else salaries[-1]

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
                "income_tax_slab": TAX_SLABS.get(company, ""),
                "payroll_payable_account": f"Payroll Payable - {info['abbr']}",
            })
            doc.insert(ignore_permissions=True)
            doc.submit()
            print(f"  Assigned {emp.employee_name}: {info['currency']} {base:,.0f}")
    frappe.db.commit()


def create_payroll_entries():
    print("Creating salary slips for January 2026...")
    for company in COMPANIES:
        info = COMPANIES[company]
        ss_name = f"Demo Payroll - {info['country']}"

        existing = frappe.db.count("Salary Slip", {
            "company": company,
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        })
        if existing:
            print(f"  {existing} salary slips already exist for {company} Jan 2026, skipping")
            continue

        employees = frappe.get_all(
            "Employee",
            filters={"company": company, "status": "Active"},
            fields=["name", "employee_name"],
            order_by="creation",
        )

        for emp in employees:
            slip = frappe.get_doc({
                "doctype": "Salary Slip",
                "employee": emp.name,
                "company": company,
                "posting_date": "2026-01-31",
                "start_date": "2026-01-01",
                "end_date": "2026-01-31",
                "payroll_frequency": "Monthly",
                "salary_structure": ss_name,
            })
            slip.insert(ignore_permissions=True)
            slip.submit()
            print(f"    Submitted: {emp.employee_name} - Net: {info['currency']} {slip.net_pay:,.0f}")

        print(f"  Completed {len(employees)} salary slips for {company}")

    frappe.db.commit()


def _ensure_fiscal_year():
    """Create Fiscal Year 2026 if it doesn't exist."""
    if not frappe.db.exists("Fiscal Year", "2026"):
        fy = frappe.get_doc({
            "doctype": "Fiscal Year",
            "year": "2026",
            "year_start_date": "2026-01-01",
            "year_end_date": "2026-12-31",
            "companies": [{"company": c} for c in COMPANIES],
        })
        fy.insert(ignore_permissions=True)
        frappe.db.commit()
        print("  Created Fiscal Year 2026")


def create_sales_invoices():
    print("Creating sales invoices...")
    for company in COMPANIES:
        info = COMPANIES[company]
        customers = CUSTOMERS[company]
        multiplier = INVOICE_MULTIPLIERS[info["currency"]]

        for i, customer_name in enumerate(customers):
            item = ITEMS[i]
            amount = SALES_BASE_AMOUNTS[i] * multiplier

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
                "set_posting_time": 1,
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
                "set_posting_time": 1,
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


def execute():
    """Create all demo data. Run: bench --site gardaworld execute payroll_africa.demo.setup_demo_data.execute"""
    print("=" * 60)
    print("Setting up Payroll Africa demo data...")
    print("=" * 60)

    _ensure_fiscal_year()
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


def teardown():
    """Remove all demo data. Run: bench --site gardaworld execute payroll_africa.demo.setup_demo_data.teardown"""
    print("Tearing down demo data...")
    frappe.flags.ignore_permissions = True

    # 1. Cancel + delete payroll entries and salary slips
    for company in COMPANIES:
        slips = frappe.get_all("Salary Slip", filters={"company": company, "docstatus": 1}, pluck="name")
        for s in slips:
            frappe.get_doc("Salary Slip", s).cancel()
        frappe.db.delete("Salary Slip", {"company": company})

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

    # 3. Delete salary structure assignments
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
