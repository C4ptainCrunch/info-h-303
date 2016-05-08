var map = L.map('homemap', { zoomControl: false }).setView([50.83906, 4.35308], 13);

var url = "https://api.mapbox.com/styles/v1/mapbox/streets-v8/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYzRwdGFpbmNydW5jaCIsImEiOiJUdWVRSENNIn0.qssi5TBLeBinBsXkZKiI6Q";

L.tileLayer(url, {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a>'
}).addTo(map);

if(navigator.geolocation) {
  function displayPos(position) {
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;
    map.setView([lat,lon], 15);
  }
  navigator.geolocation.getCurrentPosition(displayPos,function(){});
}

var markers = new L.MarkerClusterGroup({singleMarkerMode: true});


$.ajax({
    url: "/api/etablissemens/all",
    dataType: 'json', // added data type
    success: function(res) {
        res.forEach(function(elem){
            var m = L.marker([elem.lat, elem.lon]);
            m.bindPopup(elem.name);

            markers.addLayer(m);
        });
    }
});

map.addLayer(markers);
