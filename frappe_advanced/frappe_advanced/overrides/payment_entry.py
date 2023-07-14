from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from frappe_advanced.frappe_advanced.doctype.warnings.warnings import insert_warning
from frappe.utils.user import get_user_fullname

class CustomPaymentEntry(PaymentEntry):
	def validate(self):
		self.setup_party_account_field()
		self.set_missing_values()
		self.validate_payment_type()
		self.validate_party_details()
		self.set_exchange_rate()
		self.validate_mandatory()
		self.validate_reference_documents()
		self.set_tax_withholding()
		self.set_amounts()
		self.validate_amounts()
		self.apply_taxes()
		self.set_amounts_after_tax()
		self.clear_unallocated_reference_document_rows()
		self.validate_payment_against_negative_invoice()
		self.validate_transaction_reference()
		self.set_title()
		self.set_remarks()
		self.validate_duplicate_entry()
		self.validate_payment_type_with_outstanding()
		self.validate_allocated_amount()
		self.validate_paid_invoices()
		self.validate_write_off_limit()
		self.ensure_supplier_is_not_blocked()
		self.set_status()
		

	def validate_write_off_limit(self):
		write_off_limit = frappe.db.get_single_value('Advanced Settings', 'write_off_limit')

		# total_outstanding = sum(d.allocated_amount for d in self.get("references"))
		if((write_off_limit or write_off_limit != 0 ) and self.payment_type == 'Internal Transfer'):
			total = sum(d.amount for d in self.get("deductions"))
			if(total > write_off_limit and self.difference_amount == 0):
				branch = frappe.db.get_value('Account', 
                                {'name':self.paid_from},
                                ['branch'])
				employee = get_user_fullname(frappe.session.user)
				last_warning = frappe.db.exists('Warnings',
                                                       {'warning_type':'Write-Off Limit Exceeded',
                                                        'payment_entry':self.name,
														'write_off_amount_inserted':total})
				# frappe.throw(str("exist?: {0}, Name: {1}, Total: {2}".format(
				# 	last_warning,self.name,total
				# )))
				if(not last_warning):
					warning =  insert_warning(
												warning_type='Write-Off Limit Exceeded',
												branch=branch,
												payment_entry=self.name,
												account_name=self.paid_from,
												write_off_limit=write_off_limit,
												write_off_amount_inserted=total,
												employee=employee)
				frappe.throw(_("Write off must be less than or equal to {0} {1}".format(write_off_limit, self.company_currency)))

				