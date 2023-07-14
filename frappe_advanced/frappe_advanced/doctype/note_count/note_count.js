// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Note Count', {
	validate: function(frm) {
        if(frm.doc.total_field===0) {
            msgprint('لا يمكن أن يكون اجمالي الإيداع صفر');
            validated = false;
        }
	},
	fives:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("fives_sum",frm.doc.fives*5);
	       var total_sum = (frm.doc.fives_sum+
            frm.doc.tens_sum+
            frm.doc.twenties_sum+
            frm.doc.fifties_sum+
            frm.doc.hq_amount+
            frm.doc.lyd_value+
            frm.doc.note_count_amount);
	       frm.set_value("total_field",total_sum);
	    }
    },
    tens:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("tens_sum",frm.doc.tens*10);
           var total_sum = (frm.doc.fives_sum+
            frm.doc.tens_sum+
            frm.doc.twenties_sum+
            frm.doc.fifties_sum+
            frm.doc.hq_amount+
            frm.doc.lyd_value+
            frm.doc.note_count_amount);
	       frm.set_value("total_field",total_sum);
	    }
    },
    twenties:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("twenties_sum",frm.doc.twenties*20);
	       var total_sum = (frm.doc.fives_sum+
            frm.doc.tens_sum+
            frm.doc.twenties_sum+
            frm.doc.fifties_sum+
            frm.doc.hq_amount+
            frm.doc.lyd_value+
            frm.doc.note_count_amount);
	       frm.set_value("total_field",total_sum);
	    }
    },
    fifties:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("fifties_sum",frm.doc.fifties*50);
	       var total_sum = (frm.doc.fives_sum+
            frm.doc.tens_sum+
            frm.doc.twenties_sum+
            frm.doc.fifties_sum+
            frm.doc.hq_amount+
            frm.doc.lyd_value+
            frm.doc.note_count_amount);
	       frm.set_value("total_field",total_sum);
	    }
    },
    payment_type:function(frm) {
        frm.set_value("total_field",0);
        frm.set_value("fives",0);
        frm.set_value("tens",0);
        frm.set_value("twenties",0);
        frm.set_value("fifties",0);
        frm.set_value("fives_sum",0);
        frm.set_value("tens_sum",0);
        frm.set_value("twenties_sum",0);
        frm.set_value("fifties_sum",0);
        frm.clear_table("credit_list");
        frm.clear_table("cheque_list");
        frm.set_value("hq_recieved",0);
        frm.set_value("foreign_currency_check",0);
        frm.refresh_fields();
        frm.events.show_hide(frm);
    },
    is_advance:function(frm){
        if(frm.doc.is_advance){
            frm.set_value("has_advance_note_count",0);
        }
        frm.events.show_hide(frm);
    },
    has_advance_note_count:function(frm){
        frm.set_value("advanced_note_count","");
        frm.set_value("note_count_amount",0);
        frm.events.show_hide(frm);
    },
    note_count_amount:function(frm){
        if(frm.doc.payment_type.includes("نقدية")){
            var total_sum = (frm.doc.fives_sum+
                frm.doc.tens_sum+
                frm.doc.twenties_sum+
                frm.doc.fifties_sum+
                frm.doc.hq_amount+
                frm.doc.lyd_value+
                frm.doc.note_count_amount);
            frm.set_value("total_field",total_sum);
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
	    if(frm.doc.payment_type.includes("نقدية")){
            var total_sum = (frm.doc.fives_sum+
                frm.doc.tens_sum+
                frm.doc.twenties_sum+
                frm.doc.fifties_sum+
                frm.doc.hq_amount+
                frm.doc.lyd_value+
                frm.doc.note_count_amount);
	       frm.set_value("total_field",total_sum);
	    }
    },
    lyd_value:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
            var total_sum = (frm.doc.fives_sum+
                frm.doc.tens_sum+
                frm.doc.twenties_sum+
                frm.doc.fifties_sum+
                frm.doc.hq_amount+
                frm.doc.lyd_value+
                frm.doc.note_count_amount);
	       frm.set_value("total_field",total_sum);
	    }
    },
    setup: function(frm) {
        /// replace with user permissions


        // frappe.call({
        //     method: "frappe.client.get_value",
        //     args: {
        //         doctype: "Employee",
        //         fieldname: "branch",
        //         filters: {
        //             user_id: frappe.session.user
        //         }
        //     },
        //     callback: function(r) {
        //         if (r.message) {
        //             if (r.message.branch) {
        //                 // msgprint('You are only allowed Material Receipt');
        //                 frm.set_query("payment_type", function() {
        //     			return {
        //     				filters: [
        //                         ["Mode of Payment", "mode_of_payment", "like", "%"+r.message.branch+"%"]
        //     				]
        //     			}
        //     		    });
        //             }
        //         }
        //     }
        // });
	},
    show_hide:function(frm){
        frm.toggle_display("cash_section", 
            (frm.doc.payment_type && frm.doc.payment_type.includes("نقد")));
        frm.toggle_display("credit_section", 
            (frm.doc.payment_type && frm.doc.payment_type.includes("بطاق")));
        frm.toggle_display("cheque_section", 
            (frm.doc.payment_type && frm.doc.payment_type.includes("صك")));
        frm.toggle_display("foreign_currency_section", 
            (frm.doc.foreign_currency_check));
        frm.toggle_display("extra_options",
            (frm.doc.payment_type && frm.doc.payment_type.includes("نقد")));

        frm.toggle_display("advanced_note_count", 
            (frm.doc.has_advance_note_count));
        frm.toggle_display("note_count_amount", 
            (frm.doc.has_advance_note_count));
            
        frm.toggle_display("hq_amount", 
            (frm.doc.hq_recieved));
        frm.toggle_display("has_advance_note_count",
            (frm.doc.is_advance == false && frm.doc.payment_type.includes("نقد")));
        frm.toggle_display("is_advance",
            (frm.doc.has_advance_note_count == false));
    },
    
});



frappe.ui.form.on("Credit List", "credit_amount", function(frm, cdt, cdn){
    if(frm.doc.payment_type.includes("بطاقة")){
        var d = locals[cdt][cdn];
        var total = 0;
        
        frm.doc.credit_list.forEach(function(d) { total += d.credit_amount; });
        frm.set_value('total_field', total);
    }
});

frappe.ui.form.on("Cheque List", "cheque_amount", function(frm, cdt, cdn){
    if(frm.doc.payment_type.includes("صكوك")){
        var d = locals[cdt][cdn];
        var total = 0;
        
        frm.doc.cheque_list.forEach(function(d) { total += d.cheque_amount; });
        frm.set_value('total_field', total);
    }
});
