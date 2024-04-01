# Copyright (c) 2024, MadCheese and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document

from frappe.query_builder.custom import ConstantColumn
from frappe_advanced.frappe_advanced.utils.excel_utils import make_price_xlsx
from frappe.desk.query_report import build_xlsx_data
from frappe.utils import today
from pypika import CustomFunction

class EditPriceList(Document):
	pass


@frappe.whitelist()
def start_export():

	data = frappe._dict(frappe.local.form_dict)
	
	price_list = data.get("price_list")
	percentage = data.get("percentage")
	item_groups = json.loads(data.get("item_groups"))

	data = get_data(price_list, percentage, item_groups)
	xlsx_data, column_widths = build_xlsx_data(data, [], False, True)
	xlsx_file = make_price_xlsx(xlsx_data, "Prices", column_widths=column_widths)
	
	frappe.response["filename"] = f'New {price_list}' + ".xlsx"
	frappe.response["filecontent"] = xlsx_file.getvalue()
	frappe.response["type"] = "binary"

def get_data(price_list, percentage, item_groups):
	item_doc = frappe.qb.DocType("Item")
	item_price_doc = frappe.qb.DocType("Item Price")
	float_price = (item_price_doc.price_list_rate + 
				(item_price_doc.price_list_rate * percentage / 100)).as_("float_price")
	Ceiling = CustomFunction('CEILING', ['number'])
	new_price = (Ceiling(float_price / 5) * 5).as_("new_rate")

	data_qb = (frappe.qb
						.from_(item_doc)
						.from_(item_price_doc)
						.select(
							item_price_doc.name.as_("name"),
							item_price_doc.item_code.as_("item_code"),
							item_doc.item_name.as_("item_name"),
							item_doc.item_group.as_("item_group"),
							item_price_doc.price_list_rate.as_("old_rate"),
							new_price,
							ConstantColumn(f'{percentage}%%').as_("percentage"),
						)
						.where(item_doc.item_code == item_price_doc.item_code)
						.where(item_price_doc.price_list == price_list)
						)
	if item_groups:
		data_qb = data_qb.where(item_doc.item_group.isin(item_groups))

	result = data_qb.run(as_dict=True)
	
	data = {'result': result, 'columns': get_columns()}
	data = frappe._dict(data)
	return data

def get_columns():
	return [{
	'fieldname': 'name',
	'label': 'ID',
	'fieldtype': 'Data',
	'width': 115
	},{
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
	'fieldname': 'item_group',
	'label': 'التصنيف',
	'fieldtype': 'Data',
	'width': 350
	}, {
	'fieldname': 'old_rate',
	'label': 'السعر القديم',
	'fieldtype': 'Float',
	'precision': 2,
	'width': 100
	}, {
	'fieldname': 'new_rate',
	'label': 'السعر الجديد',
	'fieldtype': 'Float',
	'precision': 2,
	'width': 100
	}, {
	'fieldname': 'percentage',
	'label': 'نسبة التعديل',
	'fieldtype': 'Data',
	'precision': 2,
	'width': 100
}]