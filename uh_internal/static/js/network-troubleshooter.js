var deviceList;
var currentDevice;
var userQuery;

function performLookup(userQueryArg) {    
    userQuery =  (typeof userQueryArg === 'undefined') ? $('#deviceOrUsername').val() : userQueryArg;
    
    if (!userQuery.length) {
        $('#deviceOrUsernameGroup').addClass('has-error');
        $('#deviceOrUsernameGroup').append('<span class="help-block">Please enter a MAC Address or email address.</span>');
        return;
    }
    else {
        $('#deviceOrUsernameGroup').removeClass('has-error');
        $('#deviceOrUsernameGroup > .help-block').remove();
    }
    
    $('#lookupSpinner').css('display', '');
    $('#deviceList').html('');
    $('#deviceReport').html('');
    
    var url = DjangoReverse['network:troubleshooter_report']({
        user_query: userQuery,
    });
    
    $.get(url, function(response) {
        $('#resultsContainer').css('display', '');
        deviceList = response.device_list;
        
        if (deviceList.length) {
            for (var i=0; i < deviceList.length; ++i) {
                var newRow = '<tr device-index="' + i.toString() + '" onclick="showReport(this);"><td><strong>' + deviceList[i].mac_address + '</strong><br />' + deviceList[i].type + '</td></tr>';
                $('#deviceList').append(newRow);
            }
        }
        else {
            $('#deviceList').append('<tr><td>No devices found for ' + userQuery + '</td></tr>');
        }
        $('#lookupSpinner').css('display', 'none');
    });
}

function showReport(element) {
    $('[device-index]').removeClass('info');
    $(element).addClass('info');
    
    currentDevice = deviceList[$(element).attr('device-index')];
    $('#deviceReport').html(currentDevice.report);
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

function initializeReport(mac_address) {
    displayAirwavesChart('#bandwidth_usage_chart', DjangoReverse['network:airwaves_client_bandwidth']({'mac_address': currentDevice.mac_address }));
    initializePopovers();
    
    var addRefreshTimer = function() {
        if ($('#login-attempt-timer').text()) {
            $('#login-attempt-timer').timer('remove');
        }
        $('#login-attempt-timer').timer({
            duration: '10s',
            callback: refreshLoginAttempts,
            repeat: true,
        });
    };
    
    addRefreshTimer();
    
    $('#auto-refresh-checkbox').change(function() {
        if (this.checked) {
            addRefreshTimer();
        }
        else {
            if ($('#login-attempt-timer').text()) {
                $('#login-attempt-timer').timer('remove');
            }
        }
    });
}

function changeEndpointInfo(actionURLName, urlArguments, callback) {
    if (typeof urlArguments === 'undefined') {
        urlArguments = {};
    }
    urlArguments.mac_address = currentDevice.mac_address;
    
    var url = DjangoReverse[actionURLName](urlArguments);
    
    $.get(url, function(response) {
        if (response.success === true) {
            alert("Endpoint successfully updated.");
            if (typeof callback === 'undefined') {
                performLookup(userQuery);
            }
            else {
                callback(urlArguments);
            }
        }
        else {
            alert("Could not change endpoint.\n\nError: " + response.error);
        }
    });
}

function removeAttributeCallback(urlArguments) {
    $('[name="' + urlArguments.attribute + '"]').remove();
}

function refreshLoginAttempts() {
    var url = DjangoReverse['network:retrieve_login_attempts']({mac_address: currentDevice.mac_address});
    $('#auto-refresh-spinner').css('display', 'inline-block');
    
    $('[popover-data-url]').popover('hide');
    
    $.get(url, function(response) {
        if (response.result === "ok") {
            var tableBody = $('#login-attempt-table-body');
            tableBody.html(response.login_attempts_table_body);
            initializePopovers();
            $('#auto-refresh-spinner').css('display', 'none');
        }
    });
}

function initializePopovers() {
    $('[popover-data-url]').hover(
        function() {
            var element = $(this);
            element.off('hover');

            $.get(element.attr('popover-data-url'), function(content) {
                if (element.filter(":hover").length) {
                    element.popover({content: content,
                                placement: 'left',
                                html: true,
                                container: 'body'
                    }).popover('show');
                }
            });
        },
        function() {
            var element = $(this);
            element.popover('hide');
        }
    );
}