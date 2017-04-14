function add_duties() {
    var duties_links = ['email_link', 'ticket_manager_link', 'voicemail_link', 'printer_requests_link'];
    var duties_titles = ['Email', 'Tickets', 'Voicemail', 'Printer Requests'];
    
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
    ajaxGet(DjangoReverse['dailyduties:refresh_duties'](), function(response_context) {
        $("#email_link").attr('data-content', response_context.email_content);
        $("#ticket_manager_link").attr('data-content', response_context.tickets_content);
        $("#voicemail_link").attr('data-content', response_context.voicemail_content);
        $("#printer_requests_link").attr('data-content', response_context.printer_requests_content);
    });
}
function updateEmail() {
    updateDuty('email', 'https://outlook.office.com/owa/resnet@calpoly.edu/?offline=disabled', '_blank');
}
function updateVoicemail() {
    updateDuty('voicemail', 'https://outlook.office.com/owa/resnet@calpoly.edu/?offline=disabled', '_blank');
}
function updatePrinterRequests() {
    updateDuty('printerrequests', DjangoReverse['printerrequests:home'](), '_self');
}
function updateTickets() {
    updateDuty('tickets', 'https://calpoly.enterprisewizard.com/gui2/cas-login?KB=calpoly2&state=Main', '_blank');
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
    ajaxPost(DjangoReverse['dailyduties:update_duty'](), {"duty": duty}, function(response_context) {
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