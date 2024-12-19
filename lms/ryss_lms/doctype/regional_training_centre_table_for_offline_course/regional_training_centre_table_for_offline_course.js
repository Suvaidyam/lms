// Copyright (c) 2024, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Regional Training Centre Table for Offline Course", {
    refresh(frm) {
        apply_filter("state_name", "country_name", frm, frm.doc.country);
        apply_filter("district_name", "state_name", frm, frm.doc.state);
        apply_filter("centre_name", "district_name", frm, frm.doc.district);
    },
    country_name(frm) {
        apply_filter("state_name", "country_name", frm, frm.doc.country);
    },
    state_name(frm) {
        apply_filter("district_name", "state_name", frm, frm.doc.state);
    },
    district_name(frm) {
        apply_filter("centre_name", "district_name", frm, frm.doc.district);
    },
    country_name(frm) {
        frm.set_value({
            "state_name": "",
            "district_name": "",
            "centre_name": ""
        })
    },
    state_name(frm) {
        frm.set_value({
            "district_name": "",
            "centre_name": ""
        })
    },
    district_name(frm) {
        frm.set_value({
            "centre_name": ""
        })
    },
});