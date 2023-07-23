# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
import re 

class AdvancedSettings(Document):
	def validate(self):
		allowed = "^[0-9,. ]*$"
		isValid = re.search(allowed, self.company_cash_notes)

		if not isValid:
			frappe.throw(
				"حقل الفئات النقدية للشركة يجب ان يحتوي على أرقام أو فواصل أو نقاط عشرية فقط")
			
	def before_save(self):
		strip = self.company_cash_notes.strip(",.")
		if strip[:2] == "0,":
			strip = strip[2:]
		if strip[:3] == "0.,":
			strip = strip[3:]
		if strip[-2:] == ",0":
			strip = strip[:-2]

		self.company_cash_notes = strip