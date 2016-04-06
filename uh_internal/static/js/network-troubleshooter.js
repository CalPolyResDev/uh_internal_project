var deviceList;

function performLookup() {
    $('#lookupSpinner').css('display', 'initial');
    $('#deviceList').html('');
    $('#deviceReport').html('');
    
    var url = DjangoReverse['network:troubleshooter_report']({
        user_query: $('#deviceOrUsername').val(),
    });
    
    $.get(url, function(response) {
        deviceList = response.device_list;
        
        if (deviceList.length) {
            for (var i=0; i < deviceList.length; ++i) {
                var newRow = '<tr device-index="' + i.toString() + '" onclick="showReport(this);"><td><strong>' + deviceList[i].mac_address + '</strong><br />' + deviceList[i].type + '</td></tr>';
                $('#deviceList').append(newRow);
            }
        }
        else {
            $('#deviceList').append('<tr><td>No matching devices.</td></tr>');
        }
        $('#lookupSpinner').css('display', 'none');
    });
}

function showReport(element) {
    $('[device-index]').removeClass('info');
    $(element).addClass('info');
    
    var device = deviceList[$(element).attr('device-index')];
    $('#deviceReport').html(device.report);
}


// Prevent submit on enter and instead perform lookup.
$(document).ready(function() {
  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      performLookup();
      return false;
    }
  });
});