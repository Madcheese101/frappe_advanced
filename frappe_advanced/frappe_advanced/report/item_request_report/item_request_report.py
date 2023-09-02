# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_data(filters):
	userBranch = frappe.db.get_value("Employee", {'user_id':frappe.session.user}, ["branch"])
	warehouse, main_warehouse= frappe.db.get_value("Branch", {'name':userBranch}, ["warehouse, main_warehouse"])
	data = []
	if not userBranch:
		frappe.throw("User has no Branch Set")
	if not warehouse:
		frappe.throw("Branch has no Warehouse Set")
	if not main_warehouse:
		frappe.throw("Branch has no Main Warehouse Set")

	size_settings = frappe.db.get_all("Stock Max QTY per Size",
					filters={'parent':userBranch}, # use userBranch instead of static value
					fields=['size', 'max_qty'],
					order_by="size")
	excluded_item_groups = frappe.db.get_all("Excluded Item Groups",
					filters={'parent':userBranch}, # use userBranch instead of static value
					fields=['item_group'],
					order_by="item_group",
					pluck="item_group")
	item_groups = frappe.db.get_list("Item Group",
					filters={'parent_item_group':'سجاد','name':["not in",excluded_item_groups]},
					fields=['name'],
					order_by="name",
					pluck="name")
	clean_item_groups = tuple(item_groups)
	# for item_group in item_groups:
	for size_info in size_settings:
		if size_info.max_qty > 0:
			items_data = frappe.db.sql(
				"""
				SELECT
					i.item_code,
					i.description,
					b.actual_qty as branch_qty,
					main.actual_qty as main_qty,
					(CASE 
						WHEN main.actual_qty >= {max_qty} 
							OR main.actual_qty >= ({max_qty} - b.actual_qty) 
							THEN {max_qty} - b.actual_qty
						ELSE main.actual_qty
					END) as order_qty
				FROM
					`tabItem` i, `tabBin` b, `tabBin` main, `tabItem Variant Attribute` c
				WHERE 
					b.item_code = i.item_code
					AND main.item_code = i.item_code
					AND i.item_group in {clean_item_groups}
					AND b.warehouse = '{warehouse}'
					AND b.actual_qty < {max_qty}
					AND main.warehouse = '{main_warehouse}'
					AND main.actual_qty > 0
					AND c.attribute_value = '{size}'
					AND c.parent = i.item_code
				Group By i.description
				""".format(max_qty=size_info.max_qty,size=size_info.size,
						main_warehouse=main_warehouse, warehouse=warehouse,
						clean_item_groups=clean_item_groups),
					as_dict=1,
				)
			if items_data:
				data.extend(items_data) 
	return data

def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("الكود"),
			"fieldtype": "Data",
			"width": 130
		}
		,
		{
			"fieldname": "description",
			"label": _("الصنف"),
			"fieldtype": "Data",
			"width": 250
		}
		,
		{
			"fieldname": "branch_qty",
			"label": _("كمية الفرع"),
			"fieldtype": "Int",
			"width": 100
			# "precision": 2
		}
		,
		{
			"fieldname": "main_qty",
			"label": _("كمية المخزن"),
			"fieldtype": "Int",
			"width": 100
			# "precision": 2
		}
		,
		{
			"fieldname": "order_qty",
			"label": _("المطلوب"),
			"fieldtype": "Int",
			"width": 100,
			# "precision": 2
		}
		
	]
