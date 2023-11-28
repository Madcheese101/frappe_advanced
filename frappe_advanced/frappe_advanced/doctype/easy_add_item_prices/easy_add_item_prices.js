// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Easy Add Item Prices', {
	onload: function(frm){
		frm.get_field('attribute_price').grid.cannot_add_rows = true;
	},
	onload_post_render: function(frm) {
		// document.querySelectorAll("[data-fieldname='add_prices']")[1].style.color = 'white';
		// document.querySelectorAll("[data-fieldname='add_prices']")[1].style.backgroundColor = 'green';
		frm.get_field('add_prices').$input.addClass('btn-primary');
		frm.get_field('edit_prices').$input.addClass('btn-primary');
	},
	refresh: function(frm) {
		frm.disable_save();
	},
	item_group: function(frm){
		if (frm.doc.item_group && frm.doc.attribute){
			frm.call('fill_sizes_table')
		}else{frm.clear_table("size_price");}
		frm.refresh_fields();
	},
	attribute: function(frm){
		if (frm.doc.item_group && frm.doc.attribute){
			frm.call('fill_sizes_table')
		}else{frm.clear_table("size_price");}
		frm.refresh_fields();
	},
	add_prices: function(frm){
		frappe.call({
			doc: frm.doc,
			method:'process_prices',
			freeze: true
		});
	},
	edit_prices: function(frm){
		frappe.call({
			doc: frm.doc,
			method:'process_prices',
			freeze: true
		});
	},
	created_since_date: function(frm){
		if (frm.doc.item_group && frm.doc.attribute){
			frm.call('fill_sizes_table')
		}else{frm.clear_table("size_price");}
		frm.refresh_fields();
	}
});