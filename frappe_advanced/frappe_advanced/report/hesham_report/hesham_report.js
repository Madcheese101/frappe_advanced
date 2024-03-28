// Copyright (c) 2024, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Hesham Report"] = {
	"filters": [
		{
            fieldname:"from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -1)
        },
        {
            fieldname:"to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        },
		{
            fieldname:"view_method",
            label: __("نوع التقرير"),
            fieldtype: "Select",
            options: [
				// "",
				{
					label: __("مختصر"),
					value: "short",
				},
				{
					label: __("مفصل"),
					value: "detailed",
				},
				{
					label: __("مفصل حسب نوع الفاتورة"),
					value: "detailed_by_type",
				},
			],
            default: "short"
        },
		,
        {
            fieldname:"pos_profile",
            label: __("نقطة مبيعات"),
            fieldtype: "Link",
            options: 'POS Profile'
        },
	],
	onload: function(report) {
		report.page.add_inner_button(__("تحديث النتيجة"), function() {
            frappe.query_report.refresh();
		});
	},
	"tree":true,
	"name_field":"pos_profile",
	"parent_field":"pos_profile",
	"initial_depth":3
};
