var deviceList;

function performLookup() {
    var url = DjangoReverse['network:troubleshooter_lookup'](
                {user_input: $('#deviceOrUsername').val()});
    $.get(url, function(response) {
        deviceList = response.device_list;
        
        $('#deviceList').html();
        for (var i=0; i < deviceList.length; ++i) {
            var newRow = '<tr device_index="' + i.toString() + '" onclick="showReport(this);"><td><strong>' + deviceList[i].mac_address + '</strong><br />' + deviceList[i].type + '</td></tr>';
            $('#deviceList').append(newRow);
        }
    });
}

function showReport(element) {
    $('[device_index]').removeClass('info');
    $(element).addClass('info');
    
    var device = deviceList[$(element).attr('device_index')];
    $('#deviceReport').html(device.report);
}