// Copyright (c) 2024, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */
var d = new Date();

frappe.query_reports["Expenses Report"] = {
	"filters": [
        {
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
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
        {
            fieldname:"branch",
            label: __("Branch"),
            fieldtype: "Link",
            options: 'Branch'
        },
        {
            fieldname:"detailed",
            label: __("تقرير مفصل"),
            fieldtype: "Check",
            default: 1
        },
        {
			"fieldname": "show_remarks",
			"label": __("تضمين الملاحظات"),
			"fieldtype": "Check"
		}
	],
    onload: function(report) {
		report.page.add_inner_button(__("تحديث النتيجة"), function() {
            frappe.query_report.refresh();
		});
	},
    "tree":true,
	"name_field":"expense_name",
	"parent_field":"expense_name",
	"initial_depth":1
};
