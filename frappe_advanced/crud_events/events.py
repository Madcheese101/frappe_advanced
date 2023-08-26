from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.doctype.batch.batch import split_batch
from frappe.permissions import (
	add_user_permission
)
# set default target and source warehouses fields
# on stock entry before saving
def stock_entry_set_default_from_target(doc, method=None):
        if not doc.from_warehouse and doc.outgoing_stock_entry and doc.purpose == "Material Transfer":
                doc.from_warehouse = doc.get("items")[0].s_warehouse

def update_user_permissions_event(doc, method = None):
    doc_list = ["Mode of Payment", "Warehouse", "POS Profile"]
    if doc.doctype == "POS Profile":
        pos_users = doc.get("applicable_for_users")
        other_pos_users= frappe.get_list("POS Profile",
                                         filters={"name": ["!=", doc.name]},
                                         fields=["applicable_for_users.user as user"],
                                         pluck= "user")
        if pos_users:
            for pu in pos_users:
                if(pu.user in other_pos_users):
                    frappe.db.delete("POS Profile User", {
                        "parent": ["!=", doc.name],
                        "user": pu.user
                    })
                
                permissions_pos = frappe.db.get_value("User Permission",
                        {"user":pu.user, "allow": "POS Profile"},
                        ["for_value"]
                    )

                if(permissions_pos != doc.name):
                    permissions = frappe.db.get_list("User Permission",
                            filters={"user":pu.user, "allow": ["in",doc_list]},
                            pluck="name"
                        )
                    if permissions:
                        for p in permissions:
                            frappe.delete_doc("User Permission", p)
                    
                    for payment in doc.get("payments"):
                        add_user_permission("Mode of Payment", payment.mode_of_payment, pu.user)
                    add_user_permission("POS Profile", doc.name, pu.user)
                    add_user_permission("Warehouse", doc.warehouse, pu.user, applicable_for="Sales Invoice")
            frappe.clear_cache()