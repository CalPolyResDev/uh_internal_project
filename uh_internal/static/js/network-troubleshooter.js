var deviceList;

function performLookup() {
    var url = DjangoReverse['network:troubleshooter_report'](
                {user_query: $('#deviceOrUsername').val()});
    $('#deviceList').html('');
    $('#deviceReport').html('No device selected.');
    
    $.get(url, function(response) {
        deviceList = response.device_list;
        
        for (var i=0; i < deviceList.length; ++i) {
            var newRow = '<tr device-index="' + i.toString() + '" onclick="showReport(this);"><td><strong>' + deviceList[i].mac_address + '</strong><br />' + deviceList[i].type + '</td></tr>';
            $('#deviceList').append(newRow);
        }
    });
}

function showReport(element) {
    $('[device-index]').removeClass('info');
    $(element).addClass('info');
    
    var device = deviceList[$(element).attr('device-index')];
    $('#deviceReport').html(device.report);
}