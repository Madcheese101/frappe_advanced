from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_balance_on
from frappe.utils import today


@frappe.whitelist()
def get_current_user_defaults():
    branch, default_warehouse, default_in_transit_warehouse, letter_head = ["","","",""]
    
    if(frappe.session.user != "Administrator"):
        branch, default_warehouse, default_in_transit_warehouse = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 
                                                                                      ['branch', 'default_warehouse', 
                                                                                       'default_in_transit_warehouse'])
        letter_head = frappe.db.get_value('Branch', branch, ['letter_head'])
  
    return {"branch": branch or "",
            "default_warehouse": default_warehouse or "", 
            "default_in_transit_warehouse": default_in_transit_warehouse or "", 
            "letter_head": letter_head or ""}

@frappe.whitelist()
def set_title(title, doc_name):
    frappe.db.set_value('Stock Entry', doc_name, {
        'title': title
    })
    frappe.db.commit()
    return True

@frappe.whitelist()
def auto_close_shift():
    posawesome_exists = "posawesome" in frappe.get_installed_apps()
    if posawesome_exists:
        posProfile =  frappe.db.get_list('POS Profile',
                            pluck="name")
        if posProfile and len(posProfile) == 1:
            from posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift import (
                make_closing_shift_from_opening,
                submit_closing_shift
                )
            
            filters = {'status': 'Open', 
                    'docstatus': 1,
                    'pos_profile': posProfile[0],
                    'pos_closing_shift': ['in', ['', None]]}
            opening_shifts =  frappe.db.get_all('POS Opening Shift',
                                filters=filters,
                                pluck="name")
            
            if len(opening_shifts) > 0:
                for open_shift in opening_shifts:
                    open_doc = vars(frappe.get_doc("POS Opening Shift", open_shift))
                    closing_doc = make_closing_shift_from_opening(open_doc)
                    
                    for payment in closing_doc.payment_reconciliation:
                        payment.closing_amount = payment.expected_amount
                        payment.difference = 0
                        
                    submit_closing_shift(vars(closing_doc))
                frappe.msgprint("تم إغلاق مناوبات الموظفين")
            else:
                frappe.msgprint('لا يوجد مناوبات لإغلاقها')
        else:
            frappe.msgprint('المستخدم ليس موظف مبيعات')

@frappe.whitelist()
def get_current_balance_msg():
    # frappe.throw(today())
    msg = ''
    parent_accounts = frappe.db.get_list("Account",
                       filters={
                           'is_group': 1,
                           'account_number': ['in', [1112,1115,
                                                     1116,1117,
                                                     1119,1121]]
                           },
                       fields=['account_name', 'name'])
    
    for parent in parent_accounts:
        msg += parent.account_name + ': <br>' + '<ul>'
        child_accounts = frappe.db.get_list("Account",
                       filters={
                           'is_group': 0,
                           'parent_account': parent.name
                           },
                       fields=['account_name', 'name'])
        for child in child_accounts:
            balance = get_balance_on(child.name, today(), ignore_account_permission=True) or 0
            msg += f'<li>{child.account_name}: {frappe.format_value(balance, {"fieldtype":"Currency"})} </li>'
        msg += '</ul>'
    frappe.msgprint(msg)
