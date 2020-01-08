const xhrGet = (url) => {
    let Http = new XMLHttpRequest();
    let res;

    Http.onreadystatechange = () => {
        if (Http.readyState === XMLHttpRequest.DONE) {
            res = JSON.parse(Http.responseText);
        }
    };

    Http.open("GET", url, false);
    Http.send();

    return res;
};

const xhrDel = (url) => {
    let Http = new XMLHttpRequest();
    let res;

    Http.onreadystatechange = () => {
        if (Http.readyState === XMLHttpRequest.DONE) {
            res = JSON.parse(Http.responseText);
        }
    };

    Http.open("DELETE", url, false);
    Http.send();

    return res;
};

const xhrPost = (url,id,latitude,longitude) => {
    xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            console.log(json.ID + ", " + json.latitude + ", " + json.longitude);
        }
    };
    var data = JSON.stringify({"ID":id,"latitude":latitude,"longitude":longitude});
    xhr.send(data);
};



google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(function() {drawChart(1, 'humidity');});
google.charts.setOnLoadCallback(function() {drawChart(1, 'temperature');});
google.charts.setOnLoadCallback(function() {drawChart(1, 'soil_moisture');});

function drawChart(num, type) {

    let urlSensorId = "http://3.87.68.197:8099/sensordata/get/" + num;
    let sensorData = xhrGet(urlSensorId);

    let urlPredId = "http://3.87.68.197:8099/sensordata/get/predict/"+num+"/10/10";
    let pred = xhrGet(urlPredId);

    var data = new google.visualization.DataTable();

    data.addColumn('datetime', 'Data Time');
    data.addColumn('number', type);
    data.addColumn('number', 'Prediction');
    // plot recent 96 points, namely 24 hours
    for (let i = sensorData["result"]["length"]-96; i < sensorData["result"]["length"]; i++) {
        data.addRow([new Date(sensorData["result"][i]["Datetime"]), parseFloat(sensorData["result"][i][type]), null]);
    }

    data.addRow([new Date(pred["result"][pred["result"].length - 1]["Predict"]["Datetime"]), null, parseFloat(pred["result"][pred["result"].length - 1]["Predict"][type])])

    let title_t = "";
    if (type === "humidity")
    {
        title_t = "Humidity / %";
    }
    else if (type === "temperature")
    {
        title_t = "Temperature / C";
    }
    else if (type === "soil_moisture")
    {
        title_t = "Soil Moisture";
    }

    var options = {
        title: title_t,
        curveType: 'function',
        series: {
            0: {pointShape: 'none'},
            1: {pointSize: 20,
                pointShape: 'star'}
        },
        legend: { position: 'none' },
        height: 200,
        chartArea: {width:'90%'}
    };

    var chart = new google.visualization.LineChart(document.getElementById(type+'_chart'));

    chart.draw(data, options);
}

function drawMap(sensorData) {
    // initialize leaflet map
    var map = L.map('map').setView([40.770744, -73.967536], 13);

    // add base map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let sensorLoc = [];

    // construct sensor markers
    for (let i = 0; i < sensorData["result"]["length"]; i++) {
        sensorLoc.push(L.marker([parseFloat(sensorData["result"][i]["latitude"]), parseFloat(sensorData["result"][i]["longitude"])]).bindPopup('This is Sensor No. ' + sensorData["result"][i]["ID"]).on('click', function(e) {
            drawPlotsByNuM(i+1);
        }));
    };

    // add sensors on the map
    L.layerGroup(sensorLoc).addTo(map);
}

function drawPlotsByNuM(num) {
    drawChart(num, 'humidity');
    drawChart(num, 'temperature');
    drawChart(num, 'soil_moisture');
}

let urlSensorLoc = "http://3.87.68.197:8099/sensornumber/getall";
let sensorLoc = xhrGet(urlSensorLoc);

drawMap(sensorLoc);
