# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	userWarehouse = frappe.db.get_value("Employee", {'user_id':frappe.session.user}, ["default_warehouse"])
	data = get_data(filters, userWarehouse)
	columns = get_columns()
	return columns, data


def get_data(filters, userWarehouse):
	
	if(userWarehouse == None):
			userWarehouse=""
	parent_groups = []
	data = []
	total = get_totals(filters, userWarehouse)
	
	parent_groups = frappe.db.get_list('Item Group', filters={'parent_item_group':'Products - منتجات'}, pluck = 'name', order_by='name desc')
	
	for parent in parent_groups:
		# frappe.msgprint(str(total[parent]))
		

		child_data = frappe.db.sql("""
		SELECT
			i.item_group,
			sum(i.amount) as total_amount,
			sum(i.qty) as total_qty,
			(count(i.amount) * 100.0 / sum(count(i.amount)) over()) as percentage,
			(1) as indent,
			(0) as has_value
        FROM
            `tabSales Invoice Item` i, `tabItem Group` g, `tabSales Invoice` si
        WHERE
            g.name = i.item_group
            AND si.name = i.parent
            AND g.parent_item_group = "{parent}"
	    	AND si.posting_date >= "{from_date}"
	    	AND si.posting_date <= "{to_date}"
		    AND i.warehouse LIKE "%{warehouse}%"
        Group By i.item_group
        ORDER BY
            percentage desc"""
		.format(
			parent=parent,
			from_date=filters.get("from_date"),
			to_date=filters.get("to_date"),
			warehouse=userWarehouse)
		, as_dict=1)
		
		if child_data:
			list_head = [{"parent_item_group": parent,"total_amount":total[parent]["amount_sum"],"total_qty": total[parent]["sum_qty"],"percentage":total[parent]["percentage"],"indent":0, "has_value": True}]
			data.append(list_head[0])
			data.extend(child_data)
		
	#return data list
	return data

def get_totals(filters, userWarehouse):
	total = {}
	
	if(userWarehouse == None):
		userWarehouse=""

	data = frappe.db.sql("""
	SELECT
		(g.parent_item_group) as parent_item_group,
		sum(i.amount) as total_amount,
		sum(i.qty) as total_qty,
		(count(i.amount) * 100.0 / sum(count(i.amount)) over()) as percentage,
		(1) as indent,
		(0) as has_value
	FROM
		`tabSales Invoice Item` i, `tabItem Group` g, `tabSales Invoice` si
	WHERE
		g.name = i.item_group
		AND si.name = i.parent
		AND si.posting_date >= "{from_date}"
		AND si.posting_date <= "{to_date}"
		AND i.warehouse LIKE "%{warehouse}%"
	Group By g.parent_item_group
	ORDER BY
		percentage desc"""
	.format(
		from_date=filters.get("from_date"),
		to_date=filters.get("to_date"),
		warehouse=userWarehouse)
	, as_dict=1)
	for d in data:
		total.update({d.parent_item_group:{"amount_sum":d.total_amount,"sum_qty":d.total_qty,"percentage":d.percentage }})
	return total


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