from __future__ import unicode_literals
import frappe
from frappe import _
from frappe_advanced.frappe_advanced.doctype.warnings.warnings import insert_warning
from frappe.utils.user import get_user_fullname

# on Sales invoice Cancelled
def cancel_invoice_warning(doc, method=None):
    if frappe.db.get_single_value('Advanced Settings', 'canceled_sales_invoice_warning'):
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
    if frappe.db.get_single_value('Advanced Settings', 'partial_balance_transfer_warning'):
        role_check = "Accounts Manager" in frappe.get_roles(frappe.session.user)

        if doc.doctype == "Payment Entry" and not role_check:
            
            if(doc.payment_type == "Internal Transfer" 
            and doc.paid_from_account_balance > doc.paid_amount):
                remaining_amount = doc.paid_from_account_balance - doc.paid_amount
                employee = get_user_fullname(frappe.session.user)
                branch = frappe.get_value("Employee",{'user_id': frappe.session.user}, ['branch'])
                last_warning = frappe.db.exists('Warnings',
                                                        {'warning_type':'Partial Account Transfer',
                                                            'account_name':doc.paid_from,
                                                            'status': 'Pending Review',
                                                            'remaining_amount':remaining_amount})
                
                if(not last_warning):
                    insert_warning(warning_type="Partial Account Transfer",employee=employee,
                                branch=branch,
                                payment_entry=doc.name,
                                account_name=doc.paid_from,
                                account_balance=doc.paid_from_account_balance,
                                transferred_amount=doc.paid_amount,
                                remaining_amount=remaining_amount)

# This is called before_submit and not on validation
# since it requires the document to be saved to
# fetch its name and add it to the warnings list
def validate_write_off_limit(doc, method=None):
    if frappe.db.get_single_value('Advanced Settings', 'write_off_limit_warning'):
        role_check = "Accounts Manager" in frappe.get_roles(frappe.session.user)

        if doc.doctype == "Payment Entry" and not role_check:
            write_off_limit = frappe.db.get_single_value('Advanced Settings', 'write_off_limit')
            
            if((write_off_limit or write_off_limit != 0 ) and doc.payment_type == 'Internal Transfer'):
                total = sum(d.amount for d in doc.get("deductions"))
                
                if(total > write_off_limit and doc.difference_amount == 0):
                    branch = frappe.db.get_value('Branch Mode of Payment',
                                                  {'mode_of_payment': doc.mode_of_payment},
                                                  ['parent'])
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

def exceeded_discount_percentage(doc, method = None):
    if frappe.db.get_single_value('Advanced Settings', 'exceeded_discount_percentage'):
        role_check = "Accounts Manager" in frappe.get_roles(frappe.session.user)
        posawesome_exists = "posawesome" in frappe.get_installed_apps()

        if doc.doctype == "Sales Invoice" and not role_check and posawesome_exists:
            max_discount = frappe.db.get_value('POS Profile', doc.pos_profile, ['posa_max_discount_allowed'])
            exceeded_items = ''
            for item in doc.get("items"):
                if max_discount > 0 and item.discount_percentage > max_discount:
                    exceeded_items += "الصنف: {item_name}       التخفيض: %{discount} <br>".format(item_name=item.item_name,
                                                                                            discount=item.discount_percentage)
            if exceeded_items:
                branch = frappe.db.get_value('Branch', {'warehouse': doc.set_warehouse}, ['name'])
                employee = get_user_fullname(frappe.session.user)
                warning =  insert_warning(
                                                warning_type='Exceeded Discount Percentage',
                                                branch=branch,
                                                sales_invoice=doc.name,
                                                employee=employee,
                                                items=exceeded_items
                                                )