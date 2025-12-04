# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
from datetime import datetime, time
import frappe
from frappe import _, _dict
from pypika.analytics import Sum, Count
from frappe.query_builder.custom import ConstantColumn
from pypika.terms import Case, ValueWrapper
from pypika import Order


def execute(filters=None):
	userWarehouse = frappe.db.get_value("Employee", {'user_id':frappe.session.user}, ["default_warehouse"])
	if(userWarehouse == None):
			userWarehouse=""
	filters["warehouse"] = "%{userWarehouse}%".format(userWarehouse=userWarehouse)
	from_date = datetime.combine(
			datetime.strptime(filters.get("from_date"), "%Y-%m-%d").date(), 
			time.min)
	to_date = datetime.combine(
		datetime.strptime(filters.get("to_date"), "%Y-%m-%d").date(), 
		time.max)
	filters["from_date"] = from_date
	filters["to_date"] = to_date
	data = get_data(filters)
	columns = get_columns(filters)
	return columns, data

def get_totals(filters):
	filters["nlp"] = "%Products%"	
	sinv_item_dt = frappe.qb.DocType("Sales Invoice Item")
	group_dt = frappe.qb.DocType("Item Group")

	amount_count = Count(sinv_item_dt.amount)
	percent = (amount_count * 100.0 / Sum(amount_count).over()).as_("percentage")

	data = (frappe.qb
			.from_(sinv_item_dt)
			.from_(group_dt)
			.select(
				group_dt.parent_item_group.as_("parent_item_group"),
				Sum(sinv_item_dt.amount).as_("total_amount"),
				Sum(sinv_item_dt.qty).as_("total_qty"),
				percent,
				ValueWrapper(0, "indent"),
				ValueWrapper(1, "has_value")
			)
			.where(group_dt.name == sinv_item_dt.item_group)
			.where(sinv_item_dt.warehouse.like(filters.get("warehouse")))
			.where(sinv_item_dt.creation[filters.get("from_date"):filters.get("to_date")])
			.where(group_dt.parent_item_group.not_like(filters.get("nlp")))
			.groupby(group_dt.parent_item_group)
			.orderby(percent, order=Order.desc)
		).run(as_dict=1)
	return data

def get_data(filters):
	
	data = []
	total = get_totals(filters)

	for parent in total:
		filters["parent"] = parent.parent_item_group
		sinv_item_dt = frappe.qb.DocType("Sales Invoice Item")
		group_dt = frappe.qb.DocType("Item Group")

		amount_count = Count(sinv_item_dt.amount)
		percent = (amount_count * 100.0 / Sum(amount_count).over()).as_("percentage")
		
		child_data = (frappe.qb
				.from_(sinv_item_dt)
				.from_(group_dt)
				.select(
					sinv_item_dt.item_group.as_("parent_item_group"),
					Sum(sinv_item_dt.amount).as_("total_amount"),
					Sum(sinv_item_dt.qty).as_("total_qty"),
					percent,
					ValueWrapper(1, "has_value"),
					ValueWrapper(1, "indent")
				)
				.where(group_dt.name == sinv_item_dt.item_group)
				.where(group_dt.parent_item_group == filters["parent"])
				.where(sinv_item_dt.creation[filters.get("from_date"):filters.get("to_date")])
				.where(sinv_item_dt.warehouse.like(filters.get("warehouse")))
				.groupby(sinv_item_dt.item_group)
				.orderby(percent, order=Order.desc)
			).run(as_dict=1)
		
		# child_data = childquery #used to switch between frappe.qb result and frappe.db.sql result
		if child_data:
			data.append(parent)
			if filters.get("view_method", "short") == "short":
				data.extend(child_data)
			else: 
				data.extend(process_item_group_details(filters, child_data))
		
	#return data list
	return data

def process_item_group_details(filters, child_data):
	data = []
	for child in child_data:
		sizes = get_sales_by_attribute(filters, child.parent_item_group)
		data.append(child)
		if sizes:
			data.extend(sizes)
	return data

def get_sales_by_attribute(filters, item_group):
	data = []
	attribute_dt = frappe.qb.DocType("Item Variant Attribute")
	sinv_item_dt = frappe.qb.DocType("Sales Invoice Item")
	
	amount_count = Count(sinv_item_dt.amount)
	size_percentage = (
        amount_count * 100.0 /
        Sum(amount_count).over()
    ).as_("percentage")
	
	sizes = (
		frappe.qb.
		from_(sinv_item_dt)
		.from_(attribute_dt)
		.select(
			attribute_dt.attribute_value.as_("parent_item_group"),
			attribute_dt.attribute_value.as_("size"),
			Sum(sinv_item_dt.amount).as_("total_amount"),
			Sum(sinv_item_dt.qty).as_("total_qty"),
			size_percentage,
			ValueWrapper(0, "has_value"),
			ValueWrapper(2, "indent")
		)
		.where(attribute_dt.attribute == "المقاس")
		.where(attribute_dt.parent == sinv_item_dt.item_code)
		.where(sinv_item_dt.warehouse.like(filters.get("warehouse")))
		.where(sinv_item_dt.item_group == item_group)
		.where(sinv_item_dt.creation[filters.get("from_date"):filters.get("to_date")])
		.groupby(attribute_dt.attribute_value)
		.orderby(size_percentage, order=Order.desc)
	)

	sizes = sizes.run(as_dict=1)
	if filters.get("view_method", "size_only") == "size_only":
		return sizes
	
	for size in sizes:
		colors = get_size_color_sales(filters, item_group, size.size)
		data.append(size)
		if colors:
			data.extend(colors)

	return data

def get_size_color_sales(filters, item_group, size):
	size_attribute_dt = frappe.qb.DocType("Item Variant Attribute")
	color_attribute_dt = frappe.qb.DocType("Item Variant Attribute").as_("color_attr")
	sinv_item_dt = frappe.qb.DocType("Sales Invoice Item")
	
	amount_count = Count(sinv_item_dt.amount)
	size_percentage = (
        amount_count * 100.0 /
        Sum(amount_count).over()
    ).as_("percentage")
	
	size_colors_sales = (
		frappe.qb.
		from_(sinv_item_dt)
		.from_(size_attribute_dt)
		.from_(color_attribute_dt)
		.select(
			color_attribute_dt.attribute_value.as_("item_group"),
			Sum(sinv_item_dt.amount).as_("total_amount"),
			Sum(sinv_item_dt.qty).as_("total_qty"),
			size_percentage,
			ValueWrapper(0, "has_value"),
			ValueWrapper(3, "indent")
		)
		.where(size_attribute_dt.attribute == "المقاس")
		.where(size_attribute_dt.attribute_value == size)
		.where(size_attribute_dt.parent == sinv_item_dt.item_code)
		.where(color_attribute_dt.attribute == "اللون")
		.where(color_attribute_dt.parent == sinv_item_dt.item_code)

		.where(sinv_item_dt.warehouse.like(filters.get("warehouse")))
		.where(sinv_item_dt.item_group == item_group)
		.where(sinv_item_dt.creation[filters.get("from_date"):filters.get("to_date")])
		.groupby(color_attribute_dt.attribute_value)
		.orderby(size_percentage, order=Order.desc)
	)
	return size_colors_sales.run(as_dict=1)
def get_columns(filters):
	columns = [
		{
			"fieldname": "parent_item_group",
			"label": _("النوع"),
			"fieldtype": "Data",
			"width": 130
		}
	]

	if filters.get("view_method") == "size_color":
		columns.append({
			"fieldname": "item_group",
			"label": _("اللون"),
			"fieldtype": "Data",
			"width": 150
		})
	columns.extend([
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
			"precision": 4
		}
	])
	return columns