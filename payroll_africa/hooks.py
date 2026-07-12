app_name = "payroll_africa"
app_title = "Payroll Africa"
app_publisher = "Kimco"
app_description = "Statutory payroll deduction automation for African countries"
app_email = "dev@kimco.co.ke"
app_license = "gpl-3.0"

required_apps = ["frappe/erpnext", "frappe/hrms"]

# Includes
app_include_css = [
	"/assets/payroll_africa/css/payroll_africa.css",
	"/assets/payroll_africa/css/payroll_africa_change_log.css",
]
app_include_js = [
	"/assets/payroll_africa/js/payroll_africa_change_log.js",
	"/assets/payroll_africa/js/payroll_africa_salary_structure.js",
	"/assets/payroll_africa/js/payroll_africa_sidebar.js",
]

# Boot
extend_bootinfo = "payroll_africa.boot.extend_bootinfo"

scheduler_events = {
	"yearly": [
		"payroll_africa.tasks.notify_rate_review",
	],
}

# Regional overrides for the HRMS apply_regional_deductions hook.
from payroll_africa.engine.registry import COUNTRY_MAP

_APPLY_REGIONAL_DEDUCTIONS = "hrms.payroll.doctype.salary_slip.salary_slip.apply_regional_deductions"
_PAYROLL_AFRICA_DEDUCTIONS = "payroll_africa.engine.salary_slip.apply_regional_deductions"

regional_overrides = {
	country: {_APPLY_REGIONAL_DEDUCTIONS: _PAYROLL_AFRICA_DEDUCTIONS}
	for country in COUNTRY_MAP
}

# Installation
after_install = "payroll_africa.setup.after_install"
after_migrate = "payroll_africa.setup.after_migrate"
before_uninstall = "payroll_africa.setup.before_uninstall"

fixtures = [
	{
		"doctype": "Income Tax Slab",
		"filters": [["name", "in", ["Kenya PAYE 2025", "Uganda PAYE 2025", "Tanzania PAYE 2025", "Rwanda PAYE 2025", "Burundi PAYE 2025", "Malawi PAYE 2025", "Zambia PAYE 2025", "DRC PAYE 2025", "Nigeria PAYE 2025", "Mozambique PAYE 2025", "Angola PAYE 2025", "Ghana PAYE 2025", "Ethiopia PIT 2025", "South Africa PAYE 2025", "Egypt IT 2025", "Botswana PAYE 2025", "Morocco IR 2025", "Ivory Coast ITS 2025", "Tunisia IRPP 2025", "Namibia PAYE 2025", "Madagascar IRSA 2025"]]],
	},
]
