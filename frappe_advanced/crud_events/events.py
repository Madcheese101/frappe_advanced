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

# split batches on stock entry revceive.
# called on submit.
def split_move_batches_on_stock_entry(doc, method=None):
        new_batch_id = None

        if(doc.outgoing_stock_entry and ("عين" in doc.from_warehouse or "الرئيسي" in doc.from_warehouse)):
            for item in doc.get("items"):
                if item.batch_no:
                    item_batch = frappe.get_doc("Batch", item.batch_no)
                    if item_batch.batch_qty != item.qty:
                        batch_no = split_batch(item.batch_no, item.item_code, item.t_warehouse, item.qty, new_batch_id)

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