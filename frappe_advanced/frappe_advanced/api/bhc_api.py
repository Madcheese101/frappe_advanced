from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist()
def get_current_user_defaults():
    branch, default_warehouse, default_in_transit_warehouse, letter_head = ["","","",""]
    
    if(frappe.session.user != "Administrator"):
        branch, default_warehouse, default_in_transit_warehouse = frappe.db.get_value('Employee', {'user_id': frappe.session.user}, ['branch', 'default_warehouse', 'default_in_transit_warehouse'])
        letter_head = frappe.db.get_value('Letter Head', {'branch': branch}, ['name'])
  
    return {"branch": branch or "", "default_warehouse": default_warehouse or "", "default_in_transit_warehouse": default_in_transit_warehouse or "", "letter_head": letter_head or ""}
