function displayAirwavesChart(jquerySelector, datasourceURL) {
    var date = new Date();
    Highcharts.setOptions({
        global: {
            timezoneOffset: date.getTimezoneOffset()
        },
    });
    
    $.get(datasourceURL, function(response) {        
        $(jquerySelector).html();
        $(jquerySelector).highcharts({
            chart: {
                type: 'spline',
                backgroundColor: null,
            },
            title: {
                text: null
            },
            xAxis: {
                type: 'datetime',
                title: {
                    text: null
                }
            },
            yAxis: {
                title: {
                    text: null
                }
            },
            credits: {
                enabled: false
            },
            series: response.data,  
        });
    });
}