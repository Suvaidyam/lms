// Copyright (c) 2024, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Registration', {
    fetch_location: function (frm) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                let latitude = position.coords.latitude;
                let longitude = position.coords.longitude;
                frm.set_value('latitude', latitude);
                frm.set_value('longitude', longitude);
                let geoJSON = {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {},
                            "geometry": {
                                "type": "Point",
                                "coordinates": [longitude, latitude]
                            }
                        }
                    ]
                };
                frm.set_value('farm_geocordinats', JSON.stringify(geoJSON));
                frm.save();
            });
        } else {
            frappe.msgprint({
                title: __('Error'),
                message: __('Geolocation is not supported by this browser.'),
                indicator: 'red'
            });
        }
    }
});
