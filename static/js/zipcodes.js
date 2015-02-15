
// Google Maps init
function initialize() {
    var mapOptions = {
        //center: { lat: 37.792921, lng: -122.404162},
        center: { lat: center[0], lng: center[1]},
        //zoom: zoom,
		zoom:12
    };
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    // Construct the polygon.
    for (var zip_id in zips) {

        // for multi-path polygons
		for (var count = 0; count < zips[zip_id].length; count++)
		{
        	var paths = zips[zip_id][count].map(function (path) {
            	return path.map(function(coords) {
                	return new google.maps.LatLng(coords[1], coords[0]);
            	});
        	});
		
        	var polygon = new google.maps.Polygon({
            	paths: paths,
            	strokeColor: '#FF0000',
            	strokeOpacity: 0.8,
            	strokeWeight: 2,
            	fillColor: '#FF0000',
            	fillOpacity: 0.35
        	});
        
        	var line = new google.maps.Polyline({
            	path: [new google.maps.LatLng(userloc[0][0], userloc[0][1]), new google.maps.LatLng(userloc[1][0], userloc[1][1])],
            	strokeColor: "#000000",
            	strokeOpacity: 1.0,
            	strokeWeight: 2,
            	map:map
        	});
        /*
        var line = new google.maps.Polyline({
            path: [new google.maps.LatLng(37.79296799999999, -122.40414), new google.maps.LatLng(37.786459, -122.4052347)],
            strokeColor: "#000000",
            strokeOpacity: 1.0,
            strokeWeight: 2,
            map:map
        });*/
        	polygon.setMap(map);
        /*(37.79296799999999, -122.40414)
        (37.786459, -122.4052347)  
        (37.59771059999999, -122.2760516)
        */
		}
    }

}
google.maps.event.addDomListener(window, 'load', initialize);


