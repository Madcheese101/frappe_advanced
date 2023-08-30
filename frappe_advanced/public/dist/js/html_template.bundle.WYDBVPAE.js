(() => {
  // frappe-html:/home/frappe-user/frappe-bench/apps/frappe_advanced/frappe_advanced/public/html/print_template.html
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
//# sourceMappingURL=html_template.bundle.WYDBVPAE.js.map