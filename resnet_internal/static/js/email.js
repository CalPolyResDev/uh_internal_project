var current_mailbox = 'INBOX';
var num_search_queries_running = 0;

$(document).ready(function() {
        $('#jstree_folder_structure')
        .on('select_node.jstree', function(event, data) {
            refresh_messages(data.node.id);
        })
        .jstree({
            'core': {
                'data': {
                    'url': email_folders_url,
                    'data': function(node) {
                        return { 'id': node.text };
                    }
                },
                'themes': {
                    'name': 'proton',
                    'responsive': true
                }
            }
        });
        
        $('#email_search').keyup(_.debounce(search_messages, 1000));
        $('#email_search_clear').click(function() {
            $('#email_search').val('');
            search_messages();
        });
        refresh_messages('INBOX');
});

function get_selected_emails() {
    var rows = [];
    $('#email_table tr').filter(':has(:checkbox:checked)').each(function() {
        rows.push(this.id);
    });

    return rows;
}

function set_spinner_status(emails, status) {
    for (var index = 0; index < emails.length; ++index) {
        var checkbox = document.getElementById('checkbox_' + emails[index]);
        checkbox.style.display = status ? 'none' : 'inline';
        
        var spinner = document.getElementById('spinner_' + emails[index]); 
        spinner.style.display = status ? 'inline' : 'none';
    }
}

function refresh_messages(mailbox) {
    $('#email_search').val('');
    retrieve_messages(mailbox, '');
}

function search_messages() {
    var search_string = $('#email_search').val();
    var search_this_mailbox = $('#search_this_mailbox').is(":checked");
    if (!search_string.length) search_this_mailbox = true;
    retrieve_messages(search_this_mailbox ? current_mailbox : '', search_string);
}

function retrieve_messages(mailbox, search_string) {
    ++num_search_queries_running;
    current_mailbox = mailbox;
    $("#email_table tr:gt(0)").remove();
    $("#email_table").append('<tr id="loading_email_record"><td colspan="100" style="text-align: center;"><br /><strong>Loading...</strong></td></tr>');
    ajaxPost(email_mailbox_summary_url, {"mailbox": mailbox, "search_string": search_string}, function(response_context) {
        if (!(--num_search_queries_running)) {
            $('#mailbox_name_header').css('display', (mailbox.length > 0 ? 'none' : 'table-cell'));
            $('#loading_email_record').replaceWith(response_context.response);
            $("#refresh_button").attr("onclick","refresh_messages('" + mailbox + "');");
        }
    });
}

function array_to_ajax(array, prefix) {
    var ajax_dict = {};
    for (var index = 0; index < array.length; ++index) {
        ajax_dict[prefix + index.toString()] = array[index];
    }

    return ajax_dict;
}

function archive_selected(destination_folder) {
    var selected_messages = get_selected_emails();
    set_spinner_status(selected_messages, true);

    var post_data = array_to_ajax(selected_messages, 'message');
    post_data['destination_folder'] = destination_folder;

    ajaxPost(email_archive_url, post_data, function(response_context) {
        for (var index = 0; index < selected_messages.length; ++index) {
            $(document.getElementById(selected_messages[index])).remove();
        }
    });
}

function mark_selected_unread() {
    var selected_messages = get_selected_emails();
    set_spinner_status(selected_messages, true);
    ajaxPost(email_mark_unread_url, array_to_ajax(selected_messages, 'message'), function(response_context) {
        for (var index = 0; index < selected_messages.length; ++index) {
            $(document.getElementById(selected_messages[index])).addClass('bg-info');
        }
        set_spinner_status(selected_messages, false);
    });
}

function mark_selected_read() {
    var selected_messages = get_selected_emails();
    set_spinner_status(selected_messages, true);
    ajaxPost(email_mark_read_url, array_to_ajax(selected_messages, 'message'), function(response_context) {
        for (var index = 0; index < selected_messages.length; ++index) {
            $(document.getElementById(selected_messages[index])).removeClass('bg-info');
        }
        set_spinner_status(selected_messages, false);
    });
}

function remove_voicemail(message_uid)  {
    // Cannot use JQuery here: $ signs and other character in UUID break the query
    var archive_link = document.getElementById('archive_' + message_uid);
    archive_link.style.display = 'none';
    
    var spinner = document.getElementById('spinner_' + message_uid);
    spinner.style.display = 'block';
    
    ajaxPost(email_remove_voicemail_url, {"message_uid": message_uid}, function(response_context) {
        var row = document.getElementById('voicemail_' + message_uid);
        row.parentNode.removeChild(row);
    });
}