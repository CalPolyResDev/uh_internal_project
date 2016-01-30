var editor = '';
var attachments = [];
var attachment_details = [];
var resnet_email_regex = /[,a-zA-Z0-9 <]*resnet@calpoly\.edu[>]*/i;

$.ajaxSetup({ cache: true });

function array_to_ajax(array, prefix) {
    var ajax_dict = {};
    for (var index = 0; index < array.length; ++index) {
        ajax_dict[prefix + index.toString()] = array[index];
    }

    return ajax_dict;
}

String.prototype.rsplit = function(sep, maxsplit) { // Missing Python
    var split = this.split(sep);
    return maxsplit ? [ split.slice(0, -maxsplit).join(sep) ].concat(split.slice(-maxsplit)) : split;
};

function add_button(button_text, onclick_text, id) {
    $('#email_buttons').append('<button id="' + id + '" class="btn btn-default" type="button" onclick="' + onclick_text +'">' + button_text + '</button>');
}

function change_to_editor() {
    if (message_is_html) {
        editor = CKEDITOR.replace('email_body', {
            fullPage: true,
            allowedContent: true,
            removePlugins: 'magicline',
            extraPlugins: 'autogrow',
            autoGrow_onStartup: true
        });
        editor.setData(message_reply_html);
    }
    else {
        $('#email_body').replaceWith('<textarea name="email_editor" id="email_editor" style="min-height: 300px; min-width: 100%;">' + message_reply_plain_text + '</textarea>');
    }

    $('#to_hr').css('display', 'block');
    $('#email_jfu').css('display', 'initial');
    $('#to').replaceWith('<input type="text" id="to"><hr>');
    $('#cc').replaceWith('<input type="text" id="cc"><hr>');
    $('#subject').replaceWith('<input type="text" placeholder="Subject" style="outline: none; border: none;" class="h1" id="subject">');
    $('#reply_to').remove();
    $('#date').remove();
    $('#attachments').remove();
    $('#from_header').remove();
    $('#email_buttons').html('');
    add_button('Send', 'send_email(false);', 'send_button');
    
    add_button('Send & Archive', '', 'send_and_archive_button');
    $('#send_and_archive_button').attr('title', 'Archive To:');
    $('#send_and_archive_button').attr('data-container', 'body');
    $('#send_and_archive_button').attr('data-toggle', 'popover');
    $('#send_and_archive_button').attr('data-placement', 'bottom');
    $('#send_and_archive_button').attr('data-content', $('#send_and_archive_popover_content').html());
    $('#send_and_archive_button').popover({
        html: true
    });
    

    add_button('CC a CSD', '', 'cc_csd_button');
    $('#cc_csd_button').attr('title', 'Select Building:');
    $('#cc_csd_button').attr('data-container', 'body');
    $('#cc_csd_button').attr('data-toggle', 'popover');
    $('#cc_csd_button').attr('data-placement', 'bottom');
    $('#cc_csd_button').attr('data-content', $('#cc_csd_popover_content').html());
    var cc_csd_popover = $('#cc_csd_button').popover({
        html: true
    });
    
    // Not so clever selects...
    // Clever Selects has several issues within a popover:
    //      1. It doesn't register the event handler. The workaround is to manually add on onchange attribute to the field.
    //      2. Even then, the child field is updated in the source DOM, not in the popover. Therefore, the below code
    //         adds an observer for these changes then copies them to the popover.
    //      3. Something causes the chained_ids attribute of the parent field to be appended to everytime the parent
    //         value changes. Therefore, there is code to reset this attribute back to a singular 'id_building'. 

    $('#id_community').attr('onchange', '$(this).loadAllChainedChoices();');

    var ccCSDMutationObserver = new MutationObserver(function(mutations, observer) {
        var selected_community = $('.popover-content > div > form > fieldset > div > div > #id_community').val();
        $('#cc_csd_popover_content > div > form > fieldset > div > div > #id_community').attr('chained_ids', 'id_building');
        
        // Replacing popover content dynamically: https://github.com/twbs/bootstrap/issues/6014
        var popover = $('#cc_csd_button').data('bs.popover');
        popover.tip().find('.popover-content').html($('#cc_csd_popover_content').html());
        
        // Reselect correct community without triggering AJAX call.
        var community_field = popover.tip().find('.popover-content > div > form > fieldset > div > div > #id_community');
        var community_field_onchange = community_field.attr('onchange');
        community_field.attr('onchange', '');
        community_field.val(selected_community);
        community_field.attr('onchange', community_field_onchange);
    });
    
    ccCSDMutationObserver.observe(document.getElementById('cc_csd_popover_content'), {
        subtree: true,
        childList: true
    });
    
    
    $('#email_buttons').append('<button class="btn btn-default" type="button" id="attach_button">Attach</button>');
    $('#attach_button').popover({
        html: true,
        container: 'body',
        content: attach_button_content
    });
}

function submit_cc_csd_form() {
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

    $.ajax({
        data: { building_id: $('.popover-content > div > form > fieldset > div > div > #id_building').val() },
        type: 'POST',
        url: DjangoReverse.email_get_cc_csd(),
        success: function(response) {
            var cc = $('#cc').val();
            if (cc.length) {
                cc = cc + ', ' + response.content.email_string;
            }
            else {
                cc = response.content.email_string;
            }
            $('#cc').val(cc);
        }
    });
    
    $('#cc_csd_button').data('bs.popover').hide();
}

function reply() {
    change_to_editor();
    var subject = message_subject;
    if (subject.search(/^RE:/i) == -1) {
        subject = 'Re: ' + subject;
    }
    $('#subject').val(subject);
    if (message_reply_to.search(resnet_email_regex) != -1) {
        $('#to').val(message_to);
    }
    else {
        $('#to').val(message_reply_to + ', ' + message_to);
        $('#to').val($('#to').val().replace(resnet_email_regex, ''));
    }
}

function reply_all() {
    reply();
    $('#cc').val(message_to);
    $('#cc').val($('#cc').val().replace(resnet_email_regex, ''));
}

function forward() {
    change_to_editor();
    
    var subject = message_subject;
    if (subject.search(/^FWD:/i) == -1) {
        subject = 'Fwd: ' + subject;
    }
    $('#subject').val(subject);
}

function archive(destination_folder) {
    $.blockUI({message: '<h1>Archiving...</h1>'});

    ajaxPost(DjangoReverse.email_archive(), 
        {'message0': message_path, 
            'destination_folder': destination_folder}, 
        function(response_context) {
            $.unblockUI();
            $(parent.document.getElementById(message_path)).remove();
            parent.$('#modal').modal('hide');
    });
}

function create_ticket() {
    // Popup blocking workaround: opening new windows must be a direct
    // consequence of user action. Therefore, open the window before the ajax
    // request completes then navigate to the edit ticket url.
    var newTicketWindow = window.open('', 'newTicketWindow');
    newTicketWindow.document.body.innerHTML = '<h1>Creating Ticket...</h1>';
    
    var requestor_username = $('#ticket_requestor_username').val();
    ajaxPost(DjangoReverse.email_create_ticket(),
        {'message_path': message_path, 'requestor_username': requestor_username},
        function(response) {
            if (response['redirect_url']) {
                newTicketWindow.location.href = response['redirect_url'];
            } 
            else {
                newTicketWindow.document.body.innerHTML = '<h1>Ticket Creation Failed!</h1>';
            }
        }
    );
}

function send_email(archive_folder) {
    var to = $('#to').val();
    var cc = $('#cc').val();
    var reply_to = $('#reply_to').val();
    var subject = $('#subject').val();
    var is_html;
    var body;

    if (message_is_html) {
        is_html = true;
        body = editor.getData();
    }
    else {
        is_html = false;
        body = $('#email_editor').val();
    }
    
    var in_reply_to = '';
    if (subject.search(/^Re:/i) != -1) {
        in_reply_to = message_path;
    }
    
    $.blockUI({ message: '<h1>Sending...</h1>'});
    
    var post_dict = array_to_ajax(attachments, 'attachment');
    
    post_dict['to'] = to;
    post_dict['cc'] = cc;
    post_dict['reply_to'] = reply_to;
    post_dict['body'] = body;
    post_dict['subject'] = subject;
    post_dict['is_html'] = is_html;
    post_dict['in_reply_to'] = in_reply_to;

    ajaxPost(DjangoReverse.send_email(), post_dict, 
        function(response_context) {
            $.unblockUI();
            
            if (response_context['success']) {
                if (message_path) {
                    parent.refresh_messages(message_path.rsplit('/', 1)[0]);
                }
                if (!archive_folder) {
                    parent.$('#modal').modal('hide');
                }
                else {
                    archive(archive_folder);
                }
            }
            else {
                if (response_context['reason']) {
                    alert('Failed to send message: ' + response_context['reason']);
                }
                else {
                    alert('Failed to send message. Please try again.');
                }
            }
    });
};