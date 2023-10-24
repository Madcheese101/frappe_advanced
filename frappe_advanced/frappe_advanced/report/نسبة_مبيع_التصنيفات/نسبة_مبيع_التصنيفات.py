# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from pypika.analytics import Sum, Count
from frappe.query_builder.custom import ConstantColumn

def execute(filters=None):
	userWarehouse = frappe.db.get_value("Employee", {'user_id':frappe.session.user}, ["default_warehouse"])
	if(userWarehouse == None):
			userWarehouse=""
	filters["warehouse"] = "%{userWarehouse}%".format(userWarehouse=userWarehouse)
	data = get_data(filters)
	columns = get_columns()
	return columns, data


def get_data(filters):
	
	data = []
	total = get_totals(filters)
	
	for parent in total:
		filters["parent"] = parent.parent_item_group
		child_data = frappe.db.sql("""
		SELECT
			i.item_group,
			sum(i.amount) as total_amount,
			sum(i.qty) as total_qty,
			(count(i.amount) * 100.0 / sum(count(i.amount)) over(partition by g.parent_item_group)) as percentage,
			(1) as indent,
			(0) as has_value
        FROM
            `tabSales Invoice Item` i, `tabItem Group` g, `tabSales Invoice` si
        WHERE
            g.name = i.item_group
            AND si.name = i.parent
            AND g.parent_item_group = %(parent)s
		    AND i.warehouse LIKE %(warehouse)s
			AND si.posting_date >= %(from_date)s
	    	AND si.posting_date <= %(to_date)s
        Group By i.item_group
        ORDER BY
            percentage desc""", 
		filters,
		as_dict=1)
		
		if child_data:
			data.append(parent)
			data.extend(child_data)
		
	#return data list
	return data

def get_totals(filters):
	filters["nlp"] = "%Products%"

	data = frappe.db.sql("""
	SELECT
		(g.parent_item_group) as parent_item_group,
		sum(i.amount) as total_amount,
		sum(i.qty) as total_qty,
		(count(i.amount) * 100.0 / sum(count(i.amount)) over()) as percentage,
		(0) as indent,
		(1) as has_value
	FROM
		`tabSales Invoice Item` i, `tabItem Group` g, `tabSales Invoice` si
	WHERE
		g.name = i.item_group
		AND si.name = i.parent
		AND i.warehouse LIKE %(warehouse)s
		AND si.posting_date >= %(from_date)s
	    AND si.posting_date <= %(to_date)s
		AND g.parent_item_group not like %(nlp)s
	Group By g.parent_item_group
	ORDER BY
		percentage desc""",
		filters,
		as_dict=1)
	
	return data


def get_columns():

	return [
		# Mode of payment
		{
			"fieldname": "parent_item_group",
			"label": _("النوع"),
			"fieldtype": "Data",
			"width": 130
		}
		,
		# name
		{
			"fieldname": "item_group",
			"label": _("التصنيف"),
			"fieldtype": "Data",
			"width": 150
		}
		,
		{
			"fieldname": "total_amount",
			"label": _("إجمالي القيمة"),
			"fieldtype": "Float",
			"width": 100,
			"precision": 2
		},
		{
			"fieldname": "total_qty",
			"label": _("الكمية المباعة"),
			"fieldtype": "Float",
			"width": 100,
			"precision": 2
		}
		,
		{
			"fieldname": "percentage",
			"label": _("النسبة"),
			"fieldtype": "Percent",
			"width": 100,
			"precision": 2
		}
	]