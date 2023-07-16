let default_warehouse = null;
let default_in_transit_warehouse = null;
let branch = null;

frappe.ui.form.on('Stock Entry', {
    onload: function(frm) {
        if(!frm.doc.stock_entry_type){frm.set_value("stock_entry_type", "Material Transfer")}
        
        frappe.call({
            method:"frappe_advanced.frappe_advanced.api.bhc_api.get_current_user_defaults",
            callback: function(r) {
                default_warehouse = r.message.default_warehouse;
                default_in_transit_warehouse = r.message.default_in_transit_warehouse;
                branch = r.message.branch;
            }
        });
        if(frm.doc.outgoing_stock_entry && !frm.doc.to_warehouse && !frm.doc.docstatus){
            frm.set_value("to_warehouse",default_warehouse);
        }
	},
    stock_entry_type:function(frm) {
         // if not recieve but send!
        if(!frm.doc.outgoing_stock_entry){
            if(default_in_transit_warehouse){frm.set_value("to_warehouse",default_in_transit_warehouse);}
            frm.set_value("from_warehouse",default_warehouse);
        }
    }, 
    refresh:function(frm) {
        if(frm.doc.outgoing_stock_entry && frm.doc.docstatus){
            //  Print button with specific Print Format, here is set to (Standard)
            //  As an example
            frm.add_custom_button(__('Print Recieve Order'), function(){
                frm.print_doc("أمر إستلام", branch);
            });
        }

        
    }
    
});