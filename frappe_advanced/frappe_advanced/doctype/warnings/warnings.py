# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import frappe
from frappe import _

class Warnings(Document):
	def autoname(self):
		# prefix = '{0} - NO:'.format(self.warning_type)
		# self.name = getseries(prefix, 4)
		prefix = '{0} - .####'.format(self.warning_type)
		self.name = make_autoname(prefix)

@frappe.whitelist()
def insert_warning(warning_type,employee=None,
		   branch=None,sales_invoice=None,
		   payment_entry=None,
		   account_name=None,account_balance=None,
		   last_transfer_date=None,transferred_amount=None,
		   write_off_limit=None,write_off_amount_inserted=None):
	warning = frappe.get_doc(doctype='Warnings',
				warning_type=warning_type,
				employee=employee,
				branch=branch,
				sales_invoice=sales_invoice,
				payment_entry=payment_entry,
				account_name=account_name,
				account_balance=account_balance,
				last_transfer_date=last_transfer_date,
				transferred_amount=transferred_amount,
				write_off_limit=write_off_limit,
				write_off_amount_inserted=write_off_amount_inserted)
	warning.insert(ignore_permissions=True)
	frappe.db.commit()
	return warning