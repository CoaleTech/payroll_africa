frappe.query_reports["Rate Change Audit Trail"] = {
	filters: [
		{
			fieldname: "country",
			label: __("Country"),
			fieldtype: "Select",
			options: "\nKenya\nUganda\nTanzania\nRwanda\nBurundi\nMalawi\nZambia\nMozambique\nAngola\nNigeria\nDRC",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
