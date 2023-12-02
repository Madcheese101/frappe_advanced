# Copyright (c) 2023, MadCheese and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from frappe.query_builder.custom import ConstantColumn
from frappe_advanced.frappe_advanced.utils.excel_utils import make_xlsx
from frappe.desk.query_report import build_xlsx_data
from frappe.utils import today

class CompareStockCount(Document):
	pass

@frappe.whitelist()
def start_export():
	employee_exist = frappe.db.exists("Employee", {"user_id": frappe.session.user})

	userWarehouse, branch = [None, None]

	if employee_exist:
		userWarehouse, branch = frappe.db.get_value("Employee", 
													{'user_id':frappe.session.user}, 
													["default_warehouse", "branch"])
	tday = today()

	data = frappe._dict(frappe.local.form_dict)
	
	item_group = data.get("item_group")

	if(userWarehouse == None):
		frappe.respond_as_web_page(
				_("Error"),
				_("This user does not have a default warehouse"),
			)
		return

	data = get_data(userWarehouse, item_group)
	xlsx_data, column_widths = build_xlsx_data(data, [], False, True)
	xlsx_file = make_xlsx(xlsx_data, "الجرد", column_widths=column_widths)
	
	frappe.response["filename"] = f'جرد {branch} {tday}' + ".xlsx"
	frappe.response["filecontent"] = xlsx_file.getvalue()
	frappe.response["type"] = "binary"

def get_data(userWarehouse, item_group):
	item_doc = frappe.qb.DocType("Item")
	bin_doc = frappe.qb.DocType("Bin")
	# row = RowNumber().orderby(item_attr.attribute_value)
	# compare_col = (fn.Concat('=IF(A',row,'=B',row,',88,99)')).as_("compare")

	data_qb = (frappe.qb
						.from_(item_doc)
						.from_(bin_doc)
						.select(
							item_doc.item_code.as_("item_code"),
							item_doc.item_name.as_("item_name"),
							bin_doc.actual_qty.as_("db_qty"),
							ConstantColumn('').as_("real_qty"),
						)
						.where(item_doc.item_code == bin_doc.item_code)
						.where(bin_doc.warehouse == userWarehouse)
						.groupby(item_doc.item_code)
						.orderby(item_doc.item_name)
						)
	if item_group:
		data_qb = data_qb.where(item_doc.item_group == item_group)

	result = data_qb.run(as_dict=True)
	data = {'result': result, 'columns': get_columns()}
	data = frappe._dict(data)
	return data

def get_columns():
	return [{
		'fieldname': 'item_code',
		'label': 'كود الصنف',
		'fieldtype': 'Data',
		'width': 115
		}, {
		'fieldname': 'item_name',
		'label': 'اسم الصنف',
		'fieldtype': 'Data',
		'width': 350
		}, {
		'fieldname': 'db_qty',
		'label': 'كمية المنظومة',
		'fieldtype': 'Float',
		'precision': 2,
		'width': 100
		}, {
		'fieldname': 'real_qty',
		'label': 'كمية الواقع',
		'fieldtype': 'Float',
		'precision': 2,
		'width': 100
	}]