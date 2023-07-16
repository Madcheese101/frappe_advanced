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
