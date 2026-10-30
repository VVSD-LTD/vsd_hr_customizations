frappe.ui.form.on("Company", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(
			__("HRMS Settings"),
			() => {
				frappe.confirm(
					__(
						"This will create Leave Types, Payroll Accounts, Salary Components, Salary Structures, Employment Types, and required custom fields if they do not already exist. Continue?"
					),
					() => {
						frappe.call({
							method:
								"vsd_hr_customizations.hrms_setup.setup.apply_hrms_settings",
							args: {
								company: frm.doc.name,
							},
							freeze: true,
							freeze_message: __("Applying HRMS Settings..."),
							callback(r) {
								if (r.message) {
									frappe.msgprint({
										title: __("HRMS Settings"),
										message: r.message,
										indicator: "green",
									});
								}
							},
						});
					}
				);
			},
			__("Action")
		);
	},
});
