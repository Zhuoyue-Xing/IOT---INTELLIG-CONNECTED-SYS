function init() {
    var options = {
        width: 400,
        height: 240,
        animation:{
            duration: 1000,
            easing: 'out',
        },
        vAxis: {minValue:0, maxValue:1000}
    };
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'N');
    data.addColumn('number', 'Value');
    data.addRow(['V', 200]);

    var chart = new google.visualization.ColumnChart(
        document.getElementById('visualization'));
    var button = document.getElementById('b1');

    function drawChart() {
        // Disabling the button while the chart is drawing.
        button.disabled = true;
        google.visualization.events.addListener(chart, 'ready',
            function() {
                button.disabled = false;
            });
        chart.draw(data, options);
    }

    button.onclick = function() {
        var newValue = 1000 - data.getValue(0, 1);
        data.setValue(0, 1, newValue);
        drawChart();
    }
    drawChart();
}