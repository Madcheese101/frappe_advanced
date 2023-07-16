from __future__ import unicode_literals
import frappe
from frappe import _
from frappe_advanced.frappe_advanced.doctype.warnings.warnings import insert_warning
from frappe.utils.user import get_user_fullname

# on Sales invoice Cancelled
def insert_invoice_warning(doc, method=None):
    role_check = "Accounts Manager" in frappe.get_roles(frappe.session.user)
    if doc.doctype == "Sales Invoice" and not role_check:
        employee = get_user_fullname(frappe.session.user)
        branch = frappe.get_value("Employee",{'user_id': frappe.session.user}, ['branch'])
        
        insert_warning(warning_type="Canceled Sales Invoice",
                        employee=employee,
                        sales_invoice=doc.name,
                        branch=branch
                        )

# Called when Payment Entry is Submitted
def partial_balance_transfer(doc, method=None):
    role_check = "Accounts Manager" in frappe.get_roles(frappe.session.user)

    if doc.doctype == "Payment Entry" and not role_check:
        
        if(doc.payment_type == "Internal Transfer" 
           and doc.paid_from_account_balance > doc.paid_amount):
        
            employee = get_user_fullname(frappe.session.user)
            branch = frappe.get_value("Employee",{'user_id': frappe.session.user}, ['branch'])
            last_warning = frappe.db.exists('Warnings',
                                                       {'warning_type':'Partial Account Transfer',
                                                        'payment_entry':doc.name,
														'account_amount':doc.paid_from_account_balance,
                                                        'account_amount_transferred':doc.paid_amount,
                                                        'account_name':doc.paid_from})
            
            if(not last_warning):
                insert_warning(warning_type="Partial Account Transfer",employee=employee,
                            branch=branch,
                            payment_entry=doc.name,
                            account_name=doc.paid_from,
                            account_amount=doc.paid_from_account_balance,
                            account_amount_transferred=doc.paid_amount)

# This is called before_submit and not on validation
# since it requires the document to be saved to
# fetch its name and add it to the warnings list
def validate_write_off_limit(doc, method=None):
		write_off_limit = frappe.db.get_single_value('Advanced Settings', 'write_off_limit')

		if((write_off_limit or write_off_limit != 0 ) and doc.payment_type == 'Internal Transfer'):
			total = sum(d.amount for d in doc.get("deductions"))
			if(total > write_off_limit and doc.difference_amount == 0):
				branch = frappe.db.get_value('Account', 
                                {'name':doc.paid_from},
                                ['branch'])
				employee = get_user_fullname(frappe.session.user)
				last_warning = frappe.db.exists('Warnings',
                                                       {'warning_type':'Write-Off Limit Exceeded',
                                                        'payment_entry':doc.name,
														'write_off_amount_inserted':total})
				if(not last_warning):
					warning =  insert_warning(
												warning_type='Write-Off Limit Exceeded',
												branch=branch,
												payment_entry=doc.name,
												account_name=doc.paid_from,
												write_off_limit=write_off_limit,
												write_off_amount_inserted=total,
												employee=employee)
				frappe.throw(_("Write off must be less than or equal to {0} {1}".format(write_off_limit, doc.company_currency)))
