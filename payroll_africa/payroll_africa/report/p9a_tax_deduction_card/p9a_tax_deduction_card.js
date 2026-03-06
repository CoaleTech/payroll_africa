frappe.query_reports["P9A Tax Deduction Card"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
			get_query: function() {
				return { filters: { country: "Kenya" } };
			},
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			reqd: 1,
			get_query: function () {
				return {
					filters: {
						company: frappe.query_report.get_filter_value("company"),
					},
				};
			},
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			reqd: 1,
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
		},
	],
	onload: function(report) {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Company",
				filters: { country: "Kenya" },
				fields: ["name"],
				limit_page_length: 1,
			},
			callback: function(r) {
				if (r.message && r.message.length) {
					var company_filter = report.get_filter("company");
					if (company_filter) {
						company_filter.set_value(r.message[0].name);
					}
				}
			},
		});
	},
};
