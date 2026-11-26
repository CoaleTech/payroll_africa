app_name = "payroll_africa"
app_title = "Payroll Africa"
app_publisher = "CoaleTech"
app_description = "Statutory payroll deduction automation for African countries"
app_email = "support@coale.tech"
app_license = "gpl-3.0"

required_apps = ["frappe/erpnext", "frappe/hrms"]

add_to_apps_screen = [
	{
		"name": "payroll_africa",
		"logo": "/assets/payroll_africa/icons/africa.svg",
		"title": "Payroll Africa",
		"route": "/app/payroll-africa",  # v16 redirects /app to /desk; v15 has no /desk
		"sequence_id": 3,
	}
]

# Includes
app_include_css = ["/assets/payroll_africa/css/payroll_africa_change_log.css"]
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

# Salary Slip subclass runs the country engine from apply_regional_deductions.
# (hrms.get_region() ignores the slip's company unless a flag is set, so the
# regional_overrides hook never fires for non-system-country companies.)
override_doctype_class = {
	"Salary Slip": "payroll_africa.engine.salary_slip.PayrollAfricaSalarySlip",
}

# Installation
after_install = "payroll_africa.setup.after_install"
after_migrate = "payroll_africa.setup.after_migrate"
before_uninstall = "payroll_africa.setup.before_uninstall"

doc_events = {
	"Company": {
		"after_insert": "payroll_africa.setup.enable_country_on_company_insert",
	},
	"Payroll Entry": {
		"onload": "payroll_africa.engine.payroll_entry.add_slip_amounts",
	},
}
