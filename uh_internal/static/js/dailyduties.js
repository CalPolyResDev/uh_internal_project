function add_duties() {
    var duties_links = ['email_link', 'ticket_manager_link', 'voicemail_link'];
    var duties_titles = ['Email', 'Tickets', 'Voicemail'];
    
    for (var i=0; i < duties_links.length; ++i) {
        var link = $('#' + duties_links[i]);
        link.attr('title', duties_titles[i]);
        link.attr('data-content', 'Loading...');
        link.attr('data-toggle', 'popover');
        link.attr('data-trigger', 'hover');
    }
    
    $('[data-toggle="popover"]').popover({
        html: true,
    });
}
function refreshDuties() {
    fetch(DjangoReverse['dailyduties:refresh_duties'](), {credentials: 'include'})
        .then(function(response) { return response.json(); })
        .then(function(data) {
            for (var key in data["inner-fragments"]) {
                $(key).html(data["inner-fragments"][key]);
            }
            $("#email_link").attr('data-content', data.email_content);
            $("#ticket_manager_link").attr('data-content', data.tickets_content);
            $("#voicemail_link").attr('data-content', data.voicemail_content);
        });
}
function updateEmail() {
    updateDuty('email', 'https://outlook.office.com/owa/resnet@calpoly.edu/?offline=disabled', '_blank');
}
function updateVoicemail() {
    updateDuty('voicemail', 'https://outlook.office.com/owa/resnet@calpoly.edu/?offline=disabled', '_blank');
}
function updateTickets() {
    updateDuty('tickets', 'https://srs.calpoly.edu/gui2/cas-login?KB=calpoly2&state=Main', '_blank');
}
function updateDuty(duty, redirect_url, target) {
    if (target === '_blank') {  // Popup-Blocking Workaround
        window.open(redirect_url, target);
    }
    var csrftoken = Cookies.get('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var request = {};
    var request_header = {};
    var request_body = {};
    request_header["X-CSRFToken"] = getCookie('csrftoken');
    request_header["Content-Type"] = 'application/json'
    request_body["duty"] = duty;
    request["method"] = 'POST';
    request["headers"] = request_header;
    request["credentials"] = 'include';
    request["body"] = JSON.stringify(request_body);

    fetch(DjangoReverse['dailyduties:update_duty'](), request)
        .then(function() {
            if (redirect_url && target !== '_blank') {
                window.open(redirect_url, target);
            }
            else {
                refreshDuties();
            }
        });
}

$(document).ready(function() {
    add_duties();
    refreshDuties();
});
