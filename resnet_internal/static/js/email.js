var current_mailbox = 'INBOX';
var num_search_queries_running = 0;
var next_group_url = '';

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
        $('#search_scope_select input:radio').change(search_messages);
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
    current_mailbox = mailbox;
    retrieve_messages(mailbox, '');
}

function search_messages() {
    var search_string = $('#email_search').val();
    var search_this_mailbox = $('#search_this_mailbox').is(":checked");
    retrieve_messages(search_this_mailbox ? current_mailbox : '', search_string);
}

function retrieve_messages(mailbox, search_string) {
    ++num_search_queries_running;
    $(document).unbind('scroll');
    $("#email_table tr:gt(0)").remove();
    $("#email_table").append('<tr id="loading_email_record"><td colspan="100" style="text-align: center;"><br /><strong>Loading...</strong></td></tr>');
    // TODO: Change hardcoded URL to use django-reverse-js. 
    $.get(encodeURI('/daily_duties/email/get_mailbox_summary/'+ encodeURIComponent(mailbox) + '/' + encodeURIComponent(search_string) + '/0/'), function(response) {
        if (!(--num_search_queries_running)) {
            console.log(response.content);
            $('#mailbox_name_header').css('display', (mailbox.length > 0 ? 'none' : 'table-cell'));
            $('#loading_email_record').replaceWith(response.content.html);
            $("#refresh_button").attr("onclick","refresh_messages('" + mailbox + "');");
            next_group_url = response.content.next_group_url;
            $(document).scroll(infiniteScrollHandler);
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

// Infinite Scroll
// Source: http://dumpk.com/2013/06/02/how-to-create-infinite-scroll-with-ajax-on-jquery/

function element_in_scroll(elem)
{
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();

    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}

var infiniteScrollHandler = function(e){
    if (element_in_scroll("#email_table tbody tr:last")) {
        $(document).unbind('scroll');
        if (next_group_url) {
            $('#email_table tbody').append('<tr id="loading_additional_emails"><td style="text-align: center;" colspan="5">Loading...<img style="width: 16px; height: 16px;" src="' + spinner_url + '"></td></tr>');
            $.ajax({
                type: "GET",
                url: next_group_url
            }).done(function( response ) {
                $('#loading_additional_emails').remove();
                $("#email_table tbody").append(response.content.html);
                next_group_url = response.content.next_group_url;
                console.log(next_group_url);
                if (next_group_url) {
                    $(document).scroll(infiniteScrollHandler);
                }
            });
        }
    }
};