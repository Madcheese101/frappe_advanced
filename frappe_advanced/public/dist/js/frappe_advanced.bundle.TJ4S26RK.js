(() => {
  // ../frappe_advanced/frappe_advanced/public/js/frappe/form/custom_form.js
  frappe.ui.form.Form = class extends frappe.ui.form.Form {
    print_doc(print_format = null, branch = null) {
      frappe.db.exists("Print Format", print_format).then((result) => {
        if (result && print_format) {
          frappe.route_options = {
            frm: this,
            print_format,
            branch
          };
          frappe.set_route("print", this.doctype, this.doc.name);
        } else if (!print_format) {
          frappe.route_options = {
            frm: this,
            print_format,
            branch
          };
          frappe.set_route("print", this.doctype, this.doc.name);
        } else {
          frappe.throw("  :\u0644\u0627 \u064A\u0648\u062C\u062F \u0648\u0631\u0642\u0629 \u0637\u0628\u0627\u0639\u0629 \u0628\u0647\u0630\u0627 \u0627\u0644\u0627\u0633\u0645</br>" + print_format);
        }
      });
    }
  };

  // ../frappe_advanced/frappe_advanced/public/js/frappe/views/reports/custom_query_report.js
  frappe.views.QueryReport = class extends frappe.views.QueryReport {
    direct_print_report(letter_head = "") {
      var print_settings = locals[":Print Settings"]["Print Settings"];
      var default_letter_head = locals[":Company"] && frappe.defaults.get_default("company") ? locals[":Company"][frappe.defaults.get_default("company")]["default_letter_head"] : "";
      var with_head = letter_head || default_letter_head ? 1 : 0;
      var data = { with_letter_head: with_head, letter_head: letter_head || default_letter_head, orientation: "Portrait" };
      data = $.extend(print_settings, data);
      if (!data.with_letter_head) {
        data.letter_head = null;
      }
      if (data.letter_head) {
        data.letter_head = frappe.boot.letter_heads[print_settings.letter_head];
      }
      const custom_format = this.report_settings.html_format || null;
      const filters_html = this.get_filters_html_for_print();
      const landscape = data.orientation == "Landscape";
      this.make_access_log("Print", "PDF");
      frappe.render_grid({
        template: data.columns ? "print_grid" : custom_format,
        title: __(this.report_name),
        subtitle: filters_html,
        print_settings: data,
        landscape,
        filters: this.get_filter_values(),
        data: this.get_data_for_print(),
        columns: this.get_columns_for_print(data, custom_format),
        original_data: this.data,
        report: this
      });
    }
  };

  // frappe-html:/home/frappe-user/frappe-bench/apps/frappe_advanced/frappe_advanced/public/js/html/print_template.html
  frappe.templates["print_template"] = `<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ layout_direction }}">
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta name="description" content="">
	<meta name="author" content="">
	<title>{{ title }}</title>
	<link href="{{ base_url }}{{ frappe.assets.bundled_asset('print.bundle.css', frappe.utils.is_rtl(lang)) }}" rel="stylesheet">
	<link href="{{ base_url }}{{ frappe.assets.bundled_asset('custom_print.bundle.css', frappe.utils.is_rtl(lang)) }}" rel="stylesheet">
	<style>
		{{ print_css }}
	</style>
</head>
<body>
	<div class="print-format-gutter">
		{% if print_settings.repeat_header_footer %}
			<div id="footer-html" class="visible-pdf">
				{% if print_settings.letter_head && print_settings.letter_head.footer %}
					<div class="letter-head-footer">
						{{ print_settings.letter_head.footer }}
					</div>
				{% endif %}
				<p class="text-center small page-number visible-pdf">
					{{ __("Page {0} of {1}", [\`<span class="page"></span>\`, \`<span class="topage"></span>\`]) }}
				</p>
			</div>
		{% endif %}

		<div class="print-format {% if landscape %}landscape{% endif %}"
				{% if columns.length > 20 %}
					{% if can_use_smaller_font %}
						style="font-size: 4.0pt"
					{% endif %}
				{% endif %}
			>
			{% if print_settings.letter_head %}
			<div {% if print_settings.repeat_header_footer %} id="header-html" class="hidden-pdf" {% endif %}>
				<div class="letter-head">{{ print_settings.letter_head.header }}</div>
			</div>
			{% endif %}
			{{ content }}
		</div>
	</div>
</body>
</html>
`;
})();
//# sourceMappingURL=frappe_advanced.bundle.TJ4S26RK.js.map
