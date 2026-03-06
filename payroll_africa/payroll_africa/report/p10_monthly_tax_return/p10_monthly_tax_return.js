frappe.query_reports["P10 Monthly Tax Return"] = {
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
			get_query: function () {
				return {
					filters: {
						company: frappe.query_report.get_filter_value("company"),
					},
				};
			},
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_end(),
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
