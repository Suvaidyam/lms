// Copyright (c) 2024, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Registration", {
	refresh(frm) {
		apply_filter("state_name", "country_name", frm, frm.doc.country);
		apply_filter("district_name", "state_name", frm, frm.doc.state);
	},
	country_name(frm) {
		apply_filter("state_name", "country_name", frm, frm.doc.country);
	},
	state_name(frm) {
		apply_filter("district_name", "state_name", frm, frm.doc.state);
	},
	country_name(frm) {
		frm.set_value({
			state_name: "",
			district_name: "",
		});
	},
	state_name(frm) {
		frm.set_value({
			district_name: "",
		});
	},
	fetch_location: function (frm) {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(function (position) {
				let latitude = position.coords.latitude;
				let longitude = position.coords.longitude;
				frm.set_value("latitude", latitude);
				frm.set_value("longitude", longitude);
				let geoJSON = {
					type: "FeatureCollection",
					features: [
						{
							type: "Feature",
							properties: {},
							geometry: {
								type: "Point",
								coordinates: [longitude, latitude],
							},
						},
					],
				};
				frm.set_value("farm_geocordinats", JSON.stringify(geoJSON));
			});
		} else {
			frappe.msgprint({
				title: __("Error"),
				message: __("Geolocation is not supported by this browser."),
				indicator: "red",
			});
		}
	},
	validate: function (frm) {
		if (frm.image_uploaded) {
			frappe.validated = false;
			frm.image_uploaded = false;
		}
	},
	...[
		"photograph",
		"vo_resolution_only_for_offline_courses_in_india",
		"land_lease_or_ownership_document",
		"10th_grade_marks_sheet__passing_certificate",
	].reduce((acc, field) => {
		acc[field] = function (frm) {
			frm.image_uploaded = true;
		};
		return acc;
	}, {}),
});
