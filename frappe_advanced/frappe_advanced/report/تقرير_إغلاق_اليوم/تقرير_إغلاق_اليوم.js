// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["تقرير إغلاق اليوم"] = {
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
	]
    ,
    onload: function(report) {
		report.page.add_inner_button(__("Print Report"), function() {
            frappe.call({
                method:"frappe_advanced.frappe_advanced.api.bhc_api.get_current_user_defaults",
                callback: function(r) {
                    report.direct_print_report(r.message.letter_head);   
                }
            });
		});
	},
    "tree":true,
	"name_field":"mode_of_payment",
	"parent_field":"mode_of_payment",
	"initial_depth":2
};

// erpnext.utils.add_dimensions('تقرير إغلاق اليوم (تسليم)', 6);
