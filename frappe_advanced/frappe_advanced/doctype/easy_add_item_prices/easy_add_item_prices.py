# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import getdate
from datetime import datetime



class EasyAddItemPrices(Document):
	
	@frappe.whitelist()
	def fill_sizes_table(self):
		if self.price_list:
			item_doc = frappe.qb.DocType("Item")
			item_attr = frappe.qb.DocType("Item Variant Attribute")
			items_data_qb = (frappe.qb
							.from_(item_doc)
							.from_(item_attr)
							.select(item_attr.attribute_value.as_("attribute_value"),
									ConstantColumn(0).as_("price"))
							.where(item_doc.item_group == self.item_group)
							.where(item_doc.item_code == item_attr.parent)
							.where(item_attr.attribute == self.attribute)
							.groupby(item_attr.attribute_value)
							.orderby(item_attr.attribute_value)
							).run(as_dict=1)
			
			self.set("attribute_price",items_data_qb)

	def get_items_list(self, attribute_value):
		data = []
		item_doc = frappe.qb.DocType("Item")
		item_attr = frappe.qb.DocType("Item Variant Attribute")
		items_data_qb = (frappe.qb
                         .from_(item_doc)
                         .from_(item_attr)
                         .select(item_doc.item_code)
                        .where(item_doc.item_group == self.item_group)
                        .where(item_doc.item_code == item_attr.parent)
                        .where(item_attr.attribute == self.attribute)
                        .where(item_attr.attribute_value == attribute_value)
                        )
		if self.created_since_date:
			date = datetime.combine(getdate(self.created_since_date),
						  datetime.min.time())
			items_data_qb = items_data_qb.where(item_doc.creation >= date)
		
		data = items_data_qb.run(pluck=item_doc.item_code)
		return data
		
	def modify(self, item_code, price):
		item_price_name = frappe.db.get_value('Item Price', 
											{"item_code": item_code, "price_list": self.price_list},
											['name'])
		if item_price_name:
			doc = frappe.get_doc('Item Price', item_price_name)
			doc.price_list_rate = price
			doc.save()
		else:
			new_doc = frappe.get_doc(doctype='Item Price')
			new_doc.item_code = item_code
			new_doc.price_list = self.price_list
			new_doc.price_list_rate = price
			new_doc.insert()
		return True
	
	def add(self, item_code, price):
		done = False
		item_price_name = frappe.db.get_value('Item Price', 
											{"item_code": item_code, "price_list": self.price_list},
											['name'])
		if not item_price_name:
			new_doc = frappe.get_doc(doctype='Item Price')
			new_doc.item_code = item_code
			new_doc.price_list = self.price_list
			new_doc.price_list_rate = price
			new_doc.insert()
			done = True
		return done

	@frappe.whitelist()
	def process_prices(self):
		done_list = []
		def_msg = _(f"تمت إضافة/تعديل أسعار الأصناف حسب {self.attribute}")
		validate_required = (True if (self.price_list and
					   self.item_group and self.attribute
					   ) else False)
		
		if validate_required == False:
			frappe.throw(_("الرجاء ملئ الحقول المطلوبة"))

		for att in self.attribute_price:
			if att.price > 0:
				size_items = self.get_items_list(att.attribute_value)

				for item in size_items:
					if self.operation_type == _("Modify"):
						done = self.modify(item, att.price)
						if done : done_list.append(att.attribute_value)
					
					if self.operation_type == _("Add"):
						done = self.add(item, att.price)
						if done : done_list.append(att.attribute_value)
		

		if len(done_list) == len(self.attribute_price):
			frappe.msgprint(def_msg)
		
		if done_list and len(done_list) < len(self.attribute_price):
			def_msg += f" لكل من: <br> {done_list}"
			frappe.msgprint(def_msg)
		
		if not done_list and self.operation_type == _("Modify") :
			frappe.msgprint(_("لم يتم تعديل أسعار الأصناف لأن الأسعار تساوي صفر"))
		else:
			frappe.msgprint(_("""لم يتم إضافة أسعار الأصناف اما لأن الأسعار تساوي صفر 
				   أو لأن الصنف موجود مسبقا في قائمة الأسعار"""))

			
		
	
