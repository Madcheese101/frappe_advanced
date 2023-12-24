// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["تقرير المبيعات"] = {
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
            fieldname:"pos_profile",
            label: __("POS Profile"),
            fieldtype: "Link",
            options: 'POS Profile'
        },
        {
            fieldname:"detailed",
            label: __("تقرير مفصل"),
            fieldtype: "Check",
            on_change: function() {
                var me_val = frappe.query_report.get_filter_value('detailed');
                var grp_val = frappe.query_report.get_filter_value('group_user');
                if (grp_val && me_val){
                    frappe.query_report.set_filter_value('group_user', 0);
                }
			}
        },
        {
            fieldname:"group_user",
            label: __("مختصر حسب الموظفين"),
            fieldtype: "Check",
            on_change: function() {
                var me_val = frappe.query_report.get_filter_value('group_user');
                var det_val = frappe.query_report.get_filter_value('detailed');
                if (me_val && det_val){
                    frappe.query_report.set_filter_value('detailed', 0);
                }
			}
        }
	],
    onload: function(report) {
		report.page.add_inner_button(__("تحديث النتيجة"), function() {
            frappe.query_report.refresh();
		});
	},
    "tree":true,
	"name_field":"name",
	"parent_field":"name",
	"initial_depth":3
};
