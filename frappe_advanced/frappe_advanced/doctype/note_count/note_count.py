# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class NoteCount(Document):
	def autoname(self):
		prefix = '{0} - {1}'.format(self.mode_of_payment, self.posting_date)
		if(self.is_advance):
			prefix = '{0} - {1} (تسليم مقدم)'.format(self.mode_of_payment, self.posting_date)
		self.name = prefix


	@frappe.whitelist()
	def set_table(self):
		company_note_types = (frappe.db.get_single_value('Advanced Settings',
						   'company_cash_notes'))
		note_types = None

		if company_note_types:
			note_types = company_note_types.split(",")
		
		if not self.get("cash_table"):
			if note_types:
				for note_type in sorted(note_types):
					self.append("cash_table", {'note': note_type,'count': 0})
			else:
				self.append("cash_table", {'note': 5,'count': 0})
				self.append("cash_table", {'note': 10,'count': 0})
				self.append("cash_table", {'note': 20,'count': 0})
				self.append("cash_table", {'note': 50,'count': 0})

	
	@frappe.whitelist()
	def calculate_cash_sum(self):
		note_sum = sum(r.note_amount for r in self.get("cash_table"))
		total = note_sum + self.lyd_value + self.hq_amount
		if(self.note_count_amount and self.note_count_amount > 0):
			total += self.note_count_amount
		self.total_field = total