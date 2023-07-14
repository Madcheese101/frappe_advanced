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
	],
    "tree":true,
	"name_field":"item_group",
	"parent_field":"parent_item_group",
	"initial_depth":3
};
