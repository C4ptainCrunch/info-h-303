var map = L.map('searchmap', { zoomControl: true }).setView([50.83906, 4.35308], 13);

var url = "https://api.mapbox.com/styles/v1/mapbox/streets-v8/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYzRwdGFpbmNydW5jaCIsImEiOiJUdWVRSENNIn0.qssi5TBLeBinBsXkZKiI6Q";

L.tileLayer(url, {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a>'
}).addTo(map);

map.setView(searchdata.center, 13);

var markers = new L.MarkerClusterGroup({singleMarkerMode: true});


searchdata.points.forEach(function(elem){
    var m = L.marker([elem.lat, elem.lon]);
    m.bindPopup(elem.name);

    markers.addLayer(m);
});


map.addLayer(markers);
