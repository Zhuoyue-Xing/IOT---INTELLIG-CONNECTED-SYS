// XHR request to get sensor locations from the database server
let Http = new XMLHttpRequest();
let url = "http://3.87.68.197:8099/sensornumber/getall";

let resData;

Http.onreadystatechange = () => {
    if (Http.readyState === XMLHttpRequest.DONE) {
        resData = JSON.parse(Http.responseText);

    }
};

Http.open("GET", url, false);
Http.send();




// initialize leaflet map
var map = L.map('map').setView([40.770744, -73.967536], 13);

// add base map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let sensorLoc = [];

// construct sensor markers
for (let i = 0; i < resData["result"]["length"]; i++) {
    sensorLoc.push(L.marker([parseFloat(resData["result"][i]["latitude"]), parseFloat(resData["result"][i]["longitude"])]).bindPopup('This is Sensor No. ' + resData["result"][i]["ID"]));
};

// add sensors on the map
L.layerGroup(sensorLoc).addTo(map);