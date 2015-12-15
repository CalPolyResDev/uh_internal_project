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
    $('#buttons').append('<button id="' + id + '" class="btn btn-default" type="button" onclick="' + onclick_text +'">' + button_text + '</button>');
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
        $('#email_body').replaceWith('<textarea name="email_editor" id="email_editor" style="min-height: 300px; min-width: 100%;">{{ message.reply_plain_text|escapejs }}</textarea>');
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
    $('#buttons').html('');
    add_button('Send', 'send_email();', 'send_button');
    
    
    $('#buttons').append('<button class="btn btn-default" type="button" id="attach_button">Attach</button>');
    $('#attach_button').popover({
        html: true,
        container: 'body',
        content: attach_button_content
    });
}

function reply() {
    change_to_editor();
    var subject = message_subject;
    if (subject.search(/^RE:/i) == -1) {
        subject = 'Re: ' + subject;
    }
    $('#subject').val(subject);
    if (message_reply_to.search(resnet_email_regex) != -1) {
        $('#to').val('{{ message.to|escapejs }}');
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

    ajaxPost(email_archive_url, 
        {'message0': message_path, 
            'destination_folder': destination_folder}, 
        function(response_context) {
            $.unblockUI();
            $(parent.document.getElementById(message_path)).remove();
            parent.$.fancybox.close();
    });
}

function send_email() {
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
        in_reply_to = '{{ message.path|escapejs }}';
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

    ajaxPost(send_email_url, post_dict, 
        function(response_context) {
            $.unblockUI();
            
            if (response_context['success']) {
                if (message_path) {
                    parent.refresh_messages(message_path.rsplit('/', 1)[0]);
                }
                parent.$.fancybox.close();
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