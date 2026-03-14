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

# Document Events
doc_events = {
	"Salary Slip": {
		"validate": "payroll_africa.engine.hooks.on_salary_slip_validate",
	}
}

# Installation
after_install = "payroll_africa.setup.after_install"
after_migrate = "payroll_africa.setup.after_migrate"
before_uninstall = "payroll_africa.setup.before_uninstall"

# Fixtures
fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [["module", "=", "Payroll Africa"]],
	},
	{
		"doctype": "Income Tax Slab",
		"filters": [["name", "in", ["Kenya PAYE 2025", "Uganda PAYE 2025", "Tanzania PAYE 2025", "Rwanda PAYE 2025", "Burundi PAYE 2025", "Malawi PAYE 2025", "Zambia PAYE 2025", "DRC PAYE 2025", "Nigeria PAYE 2025", "Mozambique PAYE 2025", "Angola PAYE 2025"]]],
	},
]
