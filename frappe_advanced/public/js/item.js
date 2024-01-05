frappe.provide('erpnext.stock');
let f_actual_qty = 0;
let to_actual_qty = 0;
let item = "";
let s_warehouse = "";
let t_warehouse = "";
let transit_warehouse = "";

frappe.ui.form.on('Item', {
    refresh: async function(frm) {
		let user_defs = await frappe.call({
            method:"frappe_advanced.frappe_advanced.api.api.get_current_user_defaults"});
		s_warehouse = user_defs.message.default_warehouse;
		transit_warehouse = user_defs.message.default_in_transit_warehouse;
		t_warehouse = s_warehouse.replace("مواد", "حجز");
		item = frm.doc.item_code;

		f_actual_qty = await frappe.db.get_value('Bin',{warehouse: s_warehouse, item_code: item}, 'actual_qty').then(
			r=>{return r.message.actual_qty}
		);
		to_actual_qty = await frappe.db.get_value('Bin',{warehouse: t_warehouse, item_code: item}, 'actual_qty').then(
			r=>{return r.message.actual_qty}
		);

		if (to_actual_qty){
			frm.add_custom_button(__('ارجاع من الحجز'), function(){
				erpnext.stock.manage_hold(item, t_warehouse, s_warehouse,
					to_actual_qty, null, 0, frm);
				});

			frm.add_custom_button(__('من الحجز للنقل'), function(){
				erpnext.stock.manage_hold(item, t_warehouse, transit_warehouse,
					to_actual_qty, null, 1, frm);
			});
		}

		if (f_actual_qty){
			frm.add_custom_button(__('نقل للحجز'), function(){
				erpnext.stock.manage_hold(item, s_warehouse, t_warehouse,
						f_actual_qty, null, 0, frm);
			});
		}
    }
});

erpnext.stock.manage_hold = async function (item, source, target, actual_qty, rate, transit, frm) {
	var dialog = new frappe.ui.Dialog({
		// title: target ? __('Add Item') : __('Move Item'),
		title: __('Move Item'),
		fields: [{
			fieldname: 'branch',
			label: __('Branch'),
			fieldtype: 'Link',
			options: 'Branch',
			reqd: transit,
			hidden: !transit
		},	
		{
			fieldname: 'item_code',
			label: __('Item'),
			fieldtype: 'Link',
			options: 'Item',
			read_only: 1
		},
		{
			fieldname: 'source',
			label: __('Source Warehouse'),
			fieldtype: 'Link',
			options: 'Warehouse',
			read_only: 1
		},
		{
			fieldname: 'target',
			label: __('Target Warehouse'),
			fieldtype: 'Link',
			options: 'Warehouse',
			reqd: 1,
			get_query() {
				return {
					filters: {
						is_group: 0
					}
				}
			}
		},
		{
			fieldname: 'qty',
			label: __('Quantity'),
			reqd: 1,
			fieldtype: 'Float',
			description: __('Available {0}', [actual_qty])
		},
		{
			fieldname: 'rate',
			label: __('Rate'),
			fieldtype: 'Currency',
			hidden: 1
		},
		],
	});
	dialog.show();
	dialog.get_field('item_code').set_input(item);

	if (source) {
		dialog.get_field('source').set_input(source);
	} else {
		dialog.get_field('source').df.hidden = 1;
		dialog.get_field('source').refresh();
	}

	if (rate) {
		dialog.get_field('rate').set_value(rate);
		dialog.get_field('rate').df.hidden = 0;
		dialog.get_field('rate').refresh();
	}

	if (target) {
		dialog.get_field('target').df.read_only = 1;
		dialog.get_field('target').value = target;
		dialog.get_field('target').refresh();
	}

	dialog.set_primary_action(__('Create Stock Entry'), function () {
		if (source && (dialog.get_value("qty") == 0 || dialog.get_value("qty") > actual_qty)) {
			frappe.msgprint(__("Quantity must be greater than zero, and less or equal to {0}", [actual_qty]));
			return;
		}

		if (dialog.get_value("source") === dialog.get_value("target")) {
			frappe.msgprint(__("Source and target warehouse must be different"));
			return;
		}

		frappe.model.with_doctype('Stock Entry', function () {
			let doc = frappe.model.get_new_doc('Stock Entry');
			doc.from_warehouse = dialog.get_value('source');
			doc.to_warehouse = dialog.get_value('target');
			doc.stock_entry_type = "Material Transfer";
			if(transit == 1){
				doc.title = dialog.get_value('branch');
			}
			
            
            let row = frappe.model.add_child(doc, 'items');
			row.item_code = dialog.get_value('item_code');
			row.s_warehouse = dialog.get_value('source');
			row.t_warehouse = dialog.get_value('target');
			row.qty = dialog.get_value('qty');
			row.conversion_factor = 1;
			row.transfer_qty = dialog.get_value('qty');
			row.basic_rate = dialog.get_value('rate');

			if (transit==1){
				frappe.db.insert(doc).then(doc=>{
					frappe.set_route('Form', doc.doctype, doc.name);
				})
			}
			else{
				frappe.call('frappe_advanced.frappe_advanced.api.api.submit_doc', {
					document: doc
				}).then(r=>{
					dialog.hide();
					frm.reload_doc();
				});
			}
		});
	});
};