# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika.terms import Case

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_data(filters):
	userBranch = None
	if(frappe.session.user != "Administrator"):
		userBranch = frappe.db.get_value("Employee", {'user_id':frappe.session.user}, ["branch"])
		
	warehouse = frappe.db.get_value("Branch", {'name':userBranch}, ["warehouse"])
	main_warehouse = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
	data = []
	if not userBranch:
		frappe.throw("User has no Branch Set")
	if not warehouse:
		frappe.throw("Branch has no Warehouse Set")
	if not main_warehouse:
		frappe.throw("Default Warehouse is not set, Please set it from Stock Settings Doctype.")

	size_settings = frappe.db.get_all("Stock Max QTY per Size",
					filters={'parent':userBranch}, # use userBranch instead of static value
					fields=['size', 'max_qty'],
					order_by="size")
	excluded_item_groups = frappe.db.get_all("Item Groups Link",
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

	item_table = frappe.qb.DocType("Item")
	main = frappe.qb.DocType("Bin")
	branch = frappe.qb.DocType("Bin").as_('b')
	variant_table = frappe.qb.DocType("Item Variant Attribute")
	
	for size_info in size_settings:
		if size_info.max_qty > 0:
			items_data = (frappe.qb
			.from_(item_table)
			.from_(main).as_('main')
			.from_(branch).as_('b')
			.from_(variant_table)
			.select(
				item_table.item_code, 
				item_table.description,
				branch.actual_qty.as_('branch_qty'),
				main.actual_qty.as_('main_qty'),
				Case()
				.when((main.actual_qty >= size_info.max_qty) | 
						(main.actual_qty >= (size_info.max_qty - branch.actual_qty)), size_info.max_qty - branch.actual_qty)
				.else_(main.actual_qty).as_("order_qty")
			)
			.where(
				(main.warehouse==main_warehouse) & 
				(main.actual_qty > 0) &
				(item_table.item_code == main.item_code)
			)
			.where(
				(branch.warehouse==warehouse) & 
				(branch.actual_qty < size_info.max_qty) & 
				(item_table.item_code == branch.item_code)
			)
			.where((item_table.item_group).isin(clean_item_groups))
			.where(
				(variant_table.attribute_value == size_info.size) & 
				(item_table.item_code == variant_table.parent))
			.groupby(item_table.description)
			).run()
			
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
