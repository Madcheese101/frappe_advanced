# Copyright (c) 2024, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Expenses(Document):
	# def autoname(self):
		# self.name = make_autoname(self.naming_series + ".####")

	def on_submit(self):
		doc = frappe.new_doc('Journal Entry')
		doc.voucher_type = "Journal Entry"
		doc.user_remark = self.notes
		doc.posting_date = self.posting_date

		# money to account
		to_ = {"account":self.expense_type_account,
	 			"cost_center": self.cost_center,
				"debit_in_account_currency": self.amount}
		# money from account
		from_ = {"account":self.branch_expense_account,
	 			"cost_center": self.cost_center,
				"credit_in_account_currency": self.amount}
		
		doc.append("accounts",to_)
		doc.append("accounts",from_)

		doc.save(ignore_permissions=True)
		doc.submit()

		self.db_set('journal_entry', doc.name)

	def on_cancel(self):
		if self.journal_entry:
			doc = frappe.get_doc("Journal Entry", self.journal_entry)
			doc.cancel()
			
	def validate(self):
		if self.amount <= 0:
			frappe.throw("قيمة المصروف يجب أن تكون أكبر من صفر")

	@frappe.whitelist()
	def set_fields(self):
		branch = None
		user = frappe.session.user
		if(frappe.session.user != "Administrator"):
			branch = frappe.db.get_value('Employee', 
					   {'user_id': user}, ['branch'])
		if self.docstatus != 1:
			if branch:
				self.branch = branch
				
				branch_cost, branch_expenses = branch = frappe.db.get_value('Branch', 
						branch, ['cost_center','expenses_account'])
				self.branch_expense_account = branch_expenses
				self.cost_center = branch_cost
			else:
				frappe.msgprint("لم يتم تحديد فرع الشركة للمستخدم")