from __future__ import unicode_literals
import frappe
from frappe import _
from frappe_advanced.frappe_advanced.doctype.warnings.warnings import insert_warning
from frappe.utils.user import get_user_fullname
from erpnext.stock.doctype.batch.batch import split_batch

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
            