frappe.ready(function () {
	// Insert button below the specified field
	document.querySelector('[data-fieldname="willingness_to_provide_at_least_05_ha_12_ac"]')
		.insertAdjacentHTML('beforeend', '<button id="custom-button" class="btn btn-primary">Fetch Location</button>');

	// Create a placeholder for the map
	document.querySelector('[data-fieldname="willingness_to_provide_at_least_05_ha_12_ac"]')
		.insertAdjacentHTML('beforeend', '<div id="map-container" style="margin-top: 10px;"></div>');

	// Add click event listener for the button
	document.getElementById('custom-button').addEventListener('click', function () {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(function (position) {
				const latitude = position.coords.latitude;
				const longitude = position.coords.longitude;

				// Set latitude and longitude fields
				frappe.web_form.set_value('latitude', latitude);
				frappe.web_form.set_value('longitude', longitude);

				// Prepare GeoJSON object
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

				// Set farm_geocordinats field with GeoJSON
				frappe.web_form.set_value('farm_geocordinats', JSON.stringify(geoJSON));
				console.log("GeoJSON set in farm_geocordinats:", JSON.stringify(geoJSON));

				// Display map in the placeholder
				const map_url = `https://www.google.com/maps?q=${latitude},${longitude}&z=15&output=embed`;
				const map_html = `
					<iframe width="100%" height="300" 
						src="${map_url}" frameborder="0" 
						style="border:0" allowfullscreen>
					</iframe>`;
				document.getElementById('map-container').innerHTML = map_html;
			}, function (error) {
				frappe.msgprint(__('Error fetching location: ' + error.message));
			});
		} else {
			frappe.msgprint(__('Geolocation is not supported by your browser.'));
		}
	});
});
