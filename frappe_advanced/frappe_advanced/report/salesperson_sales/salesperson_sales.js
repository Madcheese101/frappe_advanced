// Copyright (c) 2025, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */
var d = new Date();

frappe.query_reports["Salesperson Sales"] = {
	"filters": [
		{
            fieldname:"from_date",
            label: "From Date",
            fieldtype: "Date",
            default: new Date(d.getFullYear(),d.getMonth(),1)
        },
        {
            fieldname:"to_date",
            label: "To Date",
            fieldtype: "Date",
            default: new Date(d.getFullYear(),d.getMonth()+ 1, 0)
        },
		// {
        //     fieldname:"branch",
        //     label: __("Branch"),
        //     fieldtype: "Link",
        //     options: 'Branch'
        // },
        {
            fieldname:"branch",
            label: __("Branch"),
            fieldtype: "MultiSelectList",
            // options: 'Branch'
            get_data: function() {
                return frappe.db.get_link_options('Branch');
            }
        },
        {
            fieldname:"show_cash_only",
            label: __("Cash Only?"),
            fieldtype: "Check",
            default: 1,
            change: function() {
                frappe.query_report.refresh();
            }
        }
	],
    "tree":true,
	"name_field":"branch",
	"parent_field":"branch",
	"initial_depth":1
};
