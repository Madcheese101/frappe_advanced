// Copyright (c) 2025, MadCheese and contributors
// For license information, please see license.txt
/* eslint-disable */
var d = new Date();

frappe.query_reports["Sales Overview"] = {
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
	]
	,
    "tree":true,
	"name_field":"name",
	"parent_field":"name",
	"initial_depth":2
};
