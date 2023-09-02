// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Request Report"] = {
	"filters": [

	],
	onload: function(report) {
		report.page.add_inner_button(__("Print Report"), function() {
            frappe.call({
                method:"frappe_advanced.frappe_advanced.api.api.get_current_user_defaults",
                callback: function(r) {
                    report.direct_print_report(r.message.letter_head);   
                }
            });
		});
	}
};
