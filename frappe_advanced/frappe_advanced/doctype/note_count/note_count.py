# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class NoteCount(Document):
	def autoname(self):
		prefix = '{0} - {1}'.format(self.mode_of_payment, self.posting_date)
		if(self.is_advance):
			prefix = '{0} - {1} (تسليم مقدم)'.format(self.mode_of_payment, self.posting_date)
		self.name = prefix
