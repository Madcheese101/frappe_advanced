# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
import re 

class AdvancedSettings(Document):
	def validate(self):
		if self.company_cash_notes:
			allowed = "^[0-9,. ]*$"
			isValid = re.search(allowed, self.company_cash_notes)

			if not isValid:
				frappe.throw(
					"حقل الفئات النقدية للشركة يجب ان يحتوي على أرقام أو فواصل أو نقاط عشرية فقط")
		
		# if self.account_transfer_limit_warning:
		# 	from frappe_advanced.frappe_advanced.tasks.tasks import stock_entry_check
		# 	stock_entry_check()
		
		if self.auto_split_batch:
			main_wh = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
			main_transit_wh = frappe.db.get_value('Warehouse', {'name': main_wh}, ['default_in_transit_warehouse'])
			if not main_wh:
				frappe.throw("Default Warehouse is not set.<br> Please set it in Stock Settings")
			if not main_transit_wh:
				frappe.throw("In-Transit Warehouse for the Default Warehouse is not set.")
			
	def before_save(self):
		if self.company_cash_notes:
			strip = self.company_cash_notes.strip(",.")
			if strip[:2] == "0,":
				strip = strip[2:]
			if strip[:3] == "0.,":
				strip = strip[3:]
			if strip[-2:] == ",0":
				strip = strip[:-2]

			self.company_cash_notes = strip