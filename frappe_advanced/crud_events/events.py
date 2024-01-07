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
                doc.to_warehouse = doc.get("items")[0].t_warehouse

def split_batch_on_recieve(doc, method=None):
        auto_split_enabled = frappe.db.get_single_value('Advanced Settings', 'auto_split_batch')

        if auto_split_enabled:
            new_batch_id = None
            main_wh = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
            main_transit_wh = frappe.db.get_value('Warehouse', {'name': main_wh}, ['default_in_transit_warehouse'])
            allowed_groups = frappe.db.get_all('Item Groups Link',
                                        filters={'parent':'Advanced Settings'},
                                        pluck='item_group')

            if(doc.outgoing_stock_entry and doc.from_warehouse == main_transit_wh):
                for item in doc.get("items"):
                    item_group = frappe.db.get_value('Item', {'item_code': item.item_code}, ['item_group'])
                    if item.batch_no and item_group in allowed_groups:
                        item_batch = frappe.get_doc("Batch", item.batch_no)
                        if item_batch.batch_qty != item.qty:
                            split_batch(item.batch_no, item.item_code, item.t_warehouse, item.qty, new_batch_id)

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
               roles = frappe.get_roles(pu.user)
               if "Accounts Manager" not in roles:
                    process_permissions(doc, pu.user, other_pos_users, doc_list)
            frappe.clear_cache()

def process_permissions(doc, user, other_pos_users, doc_list):
    if(user in other_pos_users):
                frappe.db.delete("POS Profile User", {
                    "parent": ["!=", doc.name],
                    "user": user
                })
            
    permissions_pos = frappe.db.get_value("User Permission",
            {"user":user, "allow": "POS Profile"},
            ["for_value"]
        )

    if(permissions_pos != doc.name):
        permissions = frappe.db.get_list("User Permission",
                filters={"user":user, "allow": ["in",doc_list]},
                pluck="name"
            )
        if permissions:
            for p in permissions:
                frappe.delete_doc("User Permission", p)
        is_accounts_user = "Accounts User" in frappe.get_roles(user)

        if is_accounts_user:
            for payment in doc.get("payments"):
                add_user_permission("Mode of Payment", payment.mode_of_payment, user)
        add_user_permission("POS Profile", doc.name, user)
        add_user_permission("Warehouse", doc.warehouse, user, applicable_for="Sales Invoice")

def check_open_posa_shifts(doc, method = None):
    posawesome_exists = "posawesome" in frappe.get_installed_apps()
    posProfile =  frappe.db.get_list('POS Profile',
                            pluck="name")
    
    if (doc.doctype == "Payment Entry" and 
        posawesome_exists and
        posProfile and 
        doc.payment_type == _("Internal Transfer") and
        len(posProfile) == 1):
        
        filters = {'status': 'Open', 
                    'docstatus': 1,
                    'pos_profile': posProfile[0],
                    'posting_date': doc.posting_date,
                    'pos_closing_shift': ['in', ['', None]]}
        opening_shifts =  frappe.db.get_all('POS Opening Shift',
                            filters=filters,
                            pluck="name")
        
        if len(opening_shifts) > 0:
             frappe.throw("الرجاء إغلاق منوابات الموظفين أولا")

@frappe.whitelist()
def generate_item_barcode(doc, method):
	
	stock_settings = frappe.get_doc('Stock Settings')
	if not stock_settings.auto_items_barcode:
		return
	
	if not stock_settings.show_barcode_field:
		frappe.msgprint(_('Make sure to Show Barcode Field from Stock Settings'))
	
	barcode = "".join("{}".format(doc.item_code).split('.'))
	barcode = "".join("{}".format(barcode).split('-'))

	if len(barcode) < 10:
		barcode = "{}{}".format("".join(['0' for i in range(10-len(barcode))]), barcode)

	doc.append('barcodes', {
		'barcode': barcode
	})

	doc.save()
	frappe.db.commit()