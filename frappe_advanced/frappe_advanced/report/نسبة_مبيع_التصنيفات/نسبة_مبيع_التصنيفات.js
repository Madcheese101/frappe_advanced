// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["نسبة مبيع التصنيفات"] = {
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
					label: __("حسب المقاس"),
					value: "size_only",
				},
				{
					label: __("حسب المقاس و اللون"),
					value: "size_color",
				},
			],
            default: "short"
        }
	],
    "tree":true,
	"name_field":"parent_item_group",
	"parent_field":"parent_item_group",
	"initial_depth":3
};
