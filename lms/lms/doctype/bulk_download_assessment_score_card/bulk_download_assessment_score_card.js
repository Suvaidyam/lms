// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Download Assessment Score Card", {
	refresh(frm) {
		// Add custom button on refresh
		frm.add_custom_button(__("Download Score Card"), function () {
			// Call your custom API endpoint
			frappe.call({
				method: "lms.api.academy.generate_bulk_score_card", // replace with your actual method path
				args: {
					semester: frm.doc.semester,
					batch: frm.doc.batch,
					district: frm.doc.district,
				},
				freeze: true, // show loading indicator
				freeze_message: __("Downloading, please wait..."),
				callback: function (r) {
					frappe.dom.unfreeze();
					if (!r.exc && r.message) {
						console.log("r.message.record", r.message.record);
						frappe.msgprint({
							title: __("Download Start"),
							message: `<a href="/app/bulk-assessment-score-card/${r.message.record}" target="_blank">Go to Bulk Assessment Score Card</a>`,
							indicator: "green",
						});
					}
				},
			});
		}).addClass("btn-primary"); // optional styling
	},
});
