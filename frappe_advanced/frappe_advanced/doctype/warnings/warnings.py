# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _

class Warnings(Document):
	pass
@frappe.whitelist()
def insert_warning(warning_type,employee=None,
		   branch=None,sales_invoice=None,
		   account_name=None,account_amount=None,
		   last_transfer_date=None,account_amount_transferred=None,
		   write_off_limit=None,write_off_amount_inserted=None):
	warning = frappe.get_doc(doctype='Warnings',
				warning_type=warning_type,
				employee=employee,
				branch=branch,
				sales_invoice=sales_invoice,
				account_name=account_name,
				account_amount=account_amount,
				last_transfer_date=last_transfer_date,
				account_amount_transferred=account_amount_transferred,
				write_off_limit=write_off_limit,
				write_off_amount_inserted=write_off_amount_inserted)
	warning.insert(ignore_permissions=True)
	frappe.db.commit()
	return warning