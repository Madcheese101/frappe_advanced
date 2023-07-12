// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Note Count', {
	// refresh: function(frm) {

	// }
	validate: function(frm) {
        if(frm.doc.total_field===0) {
            msgprint('لا يمكن أن يكون اجمالي الإيداع صفر');
            validated = false;
        }
	},
	fives:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("fives_sum",frm.doc.fives*5);
	       var total_sum = frm.doc.fives_sum+frm.doc.tens_sum+frm.doc.twenties_sum+frm.doc.fifties_sum+frm.doc.hq_amount+frm.doc.lyd_value;
	       frm.set_value("total_field",total_sum);
	       // console.log(total_sum);
	    }
    },
    tens:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("tens_sum",frm.doc.tens*10);
	       var total_sum = frm.doc.fives_sum+frm.doc.tens_sum+frm.doc.twenties_sum+frm.doc.fifties_sum+frm.doc.hq_amount+frm.doc.lyd_value;
	       frm.set_value("total_field",total_sum);
	    }
    },
    twenties:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("twenties_sum",frm.doc.twenties*20);
	       var total_sum = frm.doc.fives_sum+frm.doc.tens_sum+frm.doc.twenties_sum+frm.doc.fifties_sum+frm.doc.hq_amount+frm.doc.lyd_value;
	       frm.set_value("total_field",total_sum);
	    }
    },
    fifties:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       frm.set_value("fifties_sum",frm.doc.fifties*50);
	       var total_sum = frm.doc.fives_sum+frm.doc.tens_sum+frm.doc.twenties_sum+frm.doc.fifties_sum+frm.doc.hq_amount+frm.doc.lyd_value;
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
    },
    foreign_currency_check:function(frm){
        if(!frm.doc.foreign_currency_check){
            frm.set_value("currency_select","");
            frm.set_value("currency_value",0);
            frm.set_value("exchange_rate",0);
            frm.set_value("lyd_value",0);
        }
    },
    hq_recieved:function(frm){
        if(!frm.doc.hq_recieved){
            frm.set_value("hq_amount",0);
        }
    },
    lyd_value:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       var total_sum = frm.doc.fives_sum+frm.doc.tens_sum+frm.doc.twenties_sum+frm.doc.fifties_sum+frm.doc.lyd_value+frm.doc.hq_amount;
	       frm.set_value("total_field",total_sum);
	    }
    },
    hq_amount:function(frm) {
	    if(frm.doc.payment_type.includes("نقدية")){
	       var total_sum = frm.doc.fives_sum+frm.doc.tens_sum+frm.doc.twenties_sum+frm.doc.fifties_sum+frm.doc.lyd_value+frm.doc.hq_amount;
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
	}
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
