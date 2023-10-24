# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class StockOrderSettings(Document):
	@frappe.whitelist()
	def set_table(self):
		filters = {'parent':"المقاس"}
		existing_size = None
		if self.max_qty_per_size:
			existing_size = frappe.db.get_all('Stock Max QTY per Size',
				 fields=["size"],
				 filters={"parent": self.name},
				 order_by='size',
				 pluck="size")
			filters['attribute_value'] = ['not in',existing_size]

		size_list = frappe.db.get_all('Item Attribute Value',
				 fields=["attribute_value as size", "'0' as max_qty"],
				 filters=filters,
				 order_by='attribute_value')		
		
		if size_list:
			for size in size_list:
				self.append("max_qty_per_size", size)
		
		if size_list and existing_size:
			frappe.msgprint("تم إضافة مقاسات جديدة الى نهاية القائمة")
