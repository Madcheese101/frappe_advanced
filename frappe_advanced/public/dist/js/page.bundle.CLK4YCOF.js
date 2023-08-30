(() => {
  // ../frappe_advanced/frappe_advanced/public/js/printing/page/print/custom_print.js
  frappe.pages["print"].on_page_load = function(wrapper) {
    frappe.ui.make_app_page({
      parent: wrapper
    });
    let print_view = new frappe.ui.form.PrintView(wrapper);
    $(wrapper).bind("show", () => {
      const route = frappe.get_route();
      const doctype = route[1];
      const docname = route.slice(2).join("/");
      if (frappe.route_options && frappe.route_options.frm && frappe.route_options.print_format) {
        print_view.frm = frappe.route_options.frm.doctype ? frappe.route_options.frm : frappe.route_options.frm.frm;
        frappe.route_options.frm = null;
        print_view.direct_print_render("/printview?", print_view.frm);
      } else if (!frappe.route_options || !frappe.route_options.frm) {
        frappe.model.with_doc(doctype, docname, () => {
          let frm = { doctype, docname };
          frm.doc = frappe.get_doc(doctype, docname);
          frappe.model.with_doctype(doctype, () => {
            frm.meta = frappe.get_meta(route[1]);
            print_view.show(frm);
          });
        });
      } else {
        print_view.frm = frappe.route_options.frm.doctype ? frappe.route_options.frm : frappe.route_options.frm.frm;
        frappe.route_options.frm = null;
        print_view.show(print_view.frm);
      }
    });
  };
  frappe.ui.form.PrintView = class extends frappe.ui.form.PrintView {
    direct_letterhead() {
      let branch = frappe.route_options.branch;
      let letterhead_options = [__("No Letterhead")];
      let default_letterhead;
      let doc_letterhead = this.frm.doc.letter_head;
      return frappe.db.get_list("Letter Head", {
        filters: [["Letter Head", "name", "like", "%" + branch + "%"]],
        fields: ["name", "is_default"],
        limit: 0
      }).then((letterheads) => {
        letterheads.map((letterhead) => {
          if (letterhead.name.includes(branch))
            default_letterhead = letterhead.name;
          return letterhead_options.push(letterhead.name);
        });
        this.letterhead_selector_df.set_data(letterhead_options);
        let selected_letterhead = default_letterhead || doc_letterhead;
        if (selected_letterhead)
          this.letterhead_selector.val(selected_letterhead);
      });
    }
    direct_print_render(method, frm) {
      this.frm = frm;
      let print_format = this.get_print_format(frappe.route_options.print_format);
      this.lang_code = print_format.default_print_language || frappe.boot.lang;
      this.setup_additional_settings();
      this.direct_letterhead().then((r) => {
        let w = window.open(frappe.urllib.get_full_url(method + "doctype=" + encodeURIComponent(this.frm.doc.doctype) + "&name=" + encodeURIComponent(this.frm.doc.name) + "&trigger_print=1&format=" + encodeURIComponent(frappe.route_options.print_format) + "&no_letterhead=0&letterhead=" + encodeURIComponent(this.get_letterhead()) + "&settings=" + encodeURIComponent(JSON.stringify(this.additional_settings)) + (this.lang_code ? "&_lang=" + this.lang_code : "")));
        if (!w) {
          frappe.msgprint(__("Please enable pop-ups"));
          return;
        }
        this.go_to_form_view();
      });
    }
  };
})();
//# sourceMappingURL=page.bundle.CLK4YCOF.js.map
