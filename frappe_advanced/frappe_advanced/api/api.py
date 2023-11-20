from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist()
def get_current_user_defaults():
    branch, default_warehouse, default_in_transit_warehouse, letter_head = ["","","",""]
    
    if(frappe.session.user != "Administrator"):
        branch, default_warehouse, default_in_transit_warehouse = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 
                                                                                      ['branch', 'default_warehouse', 
                                                                                       'default_in_transit_warehouse'])
        letter_head = frappe.db.get_value('Letter Head', {'branch': branch}, ['name'])
  
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
            else:
                frappe.msgprint('لا يوجد مناوبات لإغلاقها')
        else:
            frappe.msgprint('المستخدم ليس موظف مبيعات')
