from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from erpnext.stock.doctype.serial_no.serial_no import update_serial_nos_after_submit
from erpnext.stock.doctype.batch.batch import split_batch

class CustomStockEntry(StockEntry):

    def before_save(self):
        if not self.from_warehouse and self.outgoing_stock_entry and self.purpose == "Material Transfer":
                self.from_warehouse = self.get("items")[0].s_warehouse
                                
    def on_submit(self):
        self.update_stock_ledger()

        update_serial_nos_after_submit(self, "items")
        self.update_work_order()
        self.validate_purchase_order()
        self.update_purchase_order_supplied_items()

        self.make_gl_entries()

        self.repost_future_sle_and_gle()
        self.update_cost_in_project()
        self.validate_reserved_serial_no_consumption()
        self.update_transferred_qty()
        self.update_quality_inspection()

        if self.work_order and self.purpose == "Manufacture":
            self.update_so_in_serial_number()

        if self.purpose == "Material Transfer" and self.add_to_transit:
            self.set_material_request_transfer_status("In Transit")
        if self.purpose == "Material Transfer" and self.outgoing_stock_entry:
            self.set_material_request_transfer_status("Completed")
        self.split_move_batches()

    def split_move_batches(self):
        new_batch_id = None

        if(self.outgoing_stock_entry and ("عين" in self.from_warehouse or "الرئيسي" in self.from_warehouse)):
            for item in self.get("items"):
                if item.batch_no:
                    item_batch = frappe.get_doc("Batch", item.batch_no)
                    if item_batch.batch_qty != item.qty:
                        batch_no = split_batch(item.batch_no, item.item_code, item.t_warehouse, item.qty, new_batch_id)
            