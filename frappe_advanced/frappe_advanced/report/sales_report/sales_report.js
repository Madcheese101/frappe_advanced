// Copyright (c) 2024, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */
var d = new Date();

frappe.query_reports["Sales Report"] = {
	"filters": [
        {
			fieldname:"company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
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
            fieldname:"view_method",
            label: __("نوع التقرير"),
            fieldtype: "Select",
            options: [
				// "",
				{
					label: __("مختصر"),
					value: "short",
				},
				// {
				// 	label: __("مختصر حسب الموظفين"),
				// 	value: "employee_short",
				// },
				{
					label: __("مفصل"),
					value: "detailed",
				},
			],
            default: "short"
        },
        {
            fieldname:"show_opening_entries",
            label: __("show_opening_entries"),
            fieldtype: "Check",
            default: 0,
            hidden:1
        }
	],
    onload: function(report) {
		report.page.add_inner_button(__("تحديث النتيجة"), function() {
            frappe.query_report.refresh();
		});
	},
    "tree":true,
	"name_field":"mode_of_payment",
	"parent_field":"mode_of_payment",
	"initial_depth":1
};

frappe.form.link_formatters['User'] = function(value, doc) {
	if (doc && value && doc.full_name && doc.full_name !== value && doc.name === value) {
		return  doc.full_name;
	} else if (!value && doc.doctype && doc.full_name) {
		// format blank value in child table
		return doc.name;
	} else {
		// if value is blank in report view or project name and name are the same, return as is
		return value;
	}
};