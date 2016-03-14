// Python-Style string formatting
// Source: http://stackoverflow.com/a/18234317
if (!String.prototype.format) {
    String.prototype.format = function() {
        var str = this.toString();
        if (!arguments.length)
            return str;
        var args = typeof arguments[0],
            args = (("string" == args || "number" == args) ? arguments : arguments[0]);
        for (arg in args)
            str = str.replace(RegExp("\\{" + arg + "\\}", "gi"), args[arg]);
        return str;
    }
}

// Source: http://stackoverflow.com/a/14919494
function humanTransferRate(bps) {
    var thresh = 1000
    if(Math.abs(bps) < thresh) {
        return bps + ' bps';
    }
    var units = ['kbps','Mbps','Gbps','Tbps','Pbps','Ebps','Zbps','Ybps'];
    var u = -1;
    do {
        bps /= thresh;
        ++u;
    } while(Math.abs(bps) >= thresh && u < units.length - 1);
    return bps.toFixed(1)+' '+units[u];
}

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
            tooltip: {
                formatter: function() {
                    return '<span style="color:{pointColor}">\u25CF</span> {seriesName}: <b>{value}</b><br/>'.format({
                     pointColor: this.color,
                     seriesName: this.series.name,
                     value: this.series.options.chart_type.indexOf('bps') > -1 ? humanTransferRate(this.y) : this.y,
                });},
            },
        });
    });
}