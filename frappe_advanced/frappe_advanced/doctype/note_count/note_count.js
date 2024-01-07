// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Note Count', {
	before_submit: async function(frm){
        if(frm.doc.payment_type == "Cash"){
            await new Promise(function(resolve, reject) {
                let line_one = 'لضمان أداء أفضل لقاعدة البيانات سيتم حذف الفئات ذات العدد صفر'
                let line_two = 'هل توافق على هذه العملية؟'
                frappe.confirm(line_one+'<br>'+line_two,
                    () => {
                        // action to perform if Yes is selected                   
                        frm.call('remove_zero_notes').then(r=>{
                            resolve(true); })
                    }, () => {
                        // action to perform if No is selected
                        reject();
                    })
            });
        }
    },
    validate: function(frm) {
        if(frm.doc.total_field===0) {
            msgprint('لا يمكن أن يكون اجمالي الإيداع صفر');
            validated = false;
        }
	},
    refresh: function(frm){
        frm.events.show_hide(frm);
    },
    mode_of_payment:function(frm) {
        frm.set_value("is_credit_card",0);
        frm.set_value("total_field",0);
        frm.clear_table("credit_list");
        frm.clear_table("cheque_list");
        frm.clear_table("cash_table");
        frm.set_value("hq_recieved",0);
        frm.set_value("foreign_currency_check",0);
        frm.refresh_fields();
        frm.events.show_hide(frm);

        // if (frm.doc.mode_of_payment.includes("نقد")){
        //     frm.call('set_table')
        // }

    },
    is_advance:function(frm){
        if(frm.doc.is_advance){
            frm.set_value("has_advance_note_count",0);
        }
        frm.events.show_hide(frm);
    },
    is_credit_card:function(frm){
        frm.clear_table("credit_list");
        frm.clear_table("cheque_list");
        frm.refresh_fields();
        frm.events.show_hide(frm);
    },
    has_advance_note_count:function(frm){
        frm.set_value("advanced_note_count","");
        frm.set_value("note_count_amount",0);
        frm.events.show_hide(frm);
    },
    advanced_note_count:function(frm){
        if(frm.doc.mode_of_payment.includes("نقدية")){
            frm.call('calculate_cash_sum');
        }
    },
    foreign_currency_check:function(frm){
        frm.set_value("currency_select","");
        frm.set_value("currency_value",0);
        frm.set_value("exchange_rate",0);
        frm.set_value("lyd_value",0);
        frm.events.show_hide(frm);
    },
    hq_recieved:function(frm){
        frm.set_value("hq_amount",0);
        frm.events.show_hide(frm);
    },
    hq_amount:function(frm) {
	    if(frm.doc.mode_of_payment.includes("نقدية")){
            frm.call('calculate_cash_sum');
	    }
    },
    lyd_value:function(frm) {
	    if(frm.doc.mode_of_payment.includes("نقدية")){
            frm.call('calculate_cash_sum');
	    }
    },
    setup: function(frm) {
        frm.set_query("advanced_note_count", function() {
            return {
                filters: [
                    ["Note Count", "is_advance", "=", 1],
                    ["Note Count", "payment_type", "=", "Cash"]
                ]
            }
        });
	},
    show_hide:function(frm){
        frm.toggle_display("cash_section", 
            (frm.doc.mode_of_payment && frm.doc.payment_type == "Cash"));
        frm.toggle_display("is_credit_card", 
            (frm.doc.mode_of_payment && frm.doc.payment_type == "Bank"));
        frm.toggle_display("credit_section", 
            (frm.doc.mode_of_payment && frm.doc.is_credit_card));
        frm.toggle_display("cheque_section", 
            (frm.doc.mode_of_payment && frm.doc.payment_type == "Bank" && !frm.doc.is_credit_card));
        frm.toggle_display("foreign_currency_section", 
            (frm.doc.foreign_currency_check));
        frm.toggle_display("extra_options",
            (frm.doc.mode_of_payment && frm.doc.payment_type == "Cash"));
        
        frm.toggle_display("has_advance_note_count",
            (frm.doc.is_advance == false && frm.doc.payment_type == "Cash"));
        frm.toggle_display("advanced_note_count", 
            (frm.doc.has_advance_note_count));
        frm.toggle_display("note_count_amount", 
            (frm.doc.has_advance_note_count));
            
        frm.toggle_display("hq_amount", 
            (frm.doc.hq_recieved));

        frm.toggle_display("is_advance",
            (frm.doc.has_advance_note_count == false && frm.doc.payment_type == "Cash"));


        frm.toggle_display("add_notes",
            (frm.doc.docstatus !== 1));
        frm.toggle_display("remove_notes",
            (frm.doc.docstatus !== 1));
    },
    add_notes:function(frm){
        frm.call('set_table');
    },
    remove_notes:function(frm){
        frm.clear_table("cash_table");
        frm.refresh_field('cash_table');
        frm.call('calculate_cash_sum');
    }
    
});



frappe.ui.form.on("Credit List", "credit_amount", function(frm, cdt, cdn){
    if(frm.doc.mode_of_payment.includes("بطاقة")){
        var d = locals[cdt][cdn];
        var total = 0;
        
        frm.doc.credit_list.forEach(function(d) { total += d.credit_amount; });
        frm.set_value('total_field', total);
    }
});

frappe.ui.form.on("Cheque List", "cheque_amount", function(frm, cdt, cdn){
    if(frm.doc.mode_of_payment.includes("صكوك")){
        var d = locals[cdt][cdn];
        var total = 0;
        
        frm.doc.cheque_list.forEach(function(d) { total += d.cheque_amount; });
        frm.set_value('total_field', total);
    }
});

frappe.ui.form.on('Cash Table', {
    count:function(frm, cdt, cdn){
        if(frm.doc.mode_of_payment.includes("نقد")){
            var d = locals[cdt][cdn];
            frappe.model.set_value(d.doctype, d.name, 'note_amount', (d.note * d.count));
            if(frm.doc.mode_of_payment.includes("نقدية")){
                frm.call('calculate_cash_sum');
            }
        }
    },
    cash_table_remove:function(frm){
        frm.call('calculate_cash_sum');
    }
});