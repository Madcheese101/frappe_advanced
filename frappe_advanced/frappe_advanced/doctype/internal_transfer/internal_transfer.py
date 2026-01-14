# Copyright (c) 2025, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class InternalTransfer(Document):
	
	def on_submit(self):
		self.insert_payment_entry()
	@frappe.whitelist()
	def fetch_internal_transfer_data(self):
		data = frappe.db.get_list(
			"Payment Entry",
			filters={
				"docstatus": 1,
				"posting_date": self.closing_date,
				"payment_type": "Internal Transfer",
				"paid_to": self.from_account,
			},
			fields=["name as payment_entry", "note_count", "count_total", "received_amount", "branch"],
		)
		total = sum(item.get("received_amount", 0) for item in data) if data else 0

		self.set("internal_transfer_transactions", data)
		self.day_total_amount = total

	def insert_payment_entry(self):
		payment_entry = frappe.new_doc("Payment Entry")
		payment_entry.payment_type = "Internal Transfer"
		payment_entry.posting_date = self.closing_date
		payment_entry.mode_of_payment = self.mode_of_payment
		payment_entry.paid_from = self.from_account
		payment_entry.paid_to = self.receiving_account
		payment_entry.paid_amount = self.day_total_amount
		payment_entry.received_amount = self.day_total_amount
		if self.account_type != "نقدي":
			payment_entry.reference_no = "Internal Transfer"
			payment_entry.reference_date = self.closing_date
		payment_entry.set_missing_values()
		payment_entry.insert(ignore_permissions=True)
		payment_entry.submit()
		payment_entry.add_comment("Comment", text="تم الادخال عن طريق التحويل الداخلي: {}".format(self.name))
		self.add_comment("Comment", text="تم انشاء Payment Entry للتحويل الداخلي: {}".format(payment_entry.name))
