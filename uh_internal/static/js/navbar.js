$("#drawer").collapse();

$("#drawer-trigger").on("click", function() {
    if (window.innerWidth < 768) {
        $("#drawer").collapse("toggle");
    }
});

$(window).on("load resize", function() {
    if (window.innerWidth < 768) {
        $("#drawer").collapse("hide");
    } else {
        $("#drawer").collapse("show");
    }
});

$('#drawer').on('hidden.bs.collapse', function() {
    $("#drawer-trigger .glyphicon").removeClass("glyphicon-menu-up");

    if (window.innerWidth < 768) {
        $("#drawer-trigger .glyphicon").addClass("glyphicon-menu-down");
    }
});

$('#drawer').on('shown.bs.collapse', function() {
    $("#drawer-trigger .glyphicon").removeClass("glyphicon-menu-down");

    if (window.innerWidth < 768) {
        $("#drawer-trigger .glyphicon").addClass("glyphicon-menu-up");
    } else {
        $("#drawer-trigger .glyphicon").removeClass("glyphicon-menu-up");
    }
});

 $(".collapsable").on('hidden.bs.collapse', function(event) {
    var trigger_id = $(event.target).attr("id").replace("_list", "_link");
    $('#' + trigger_id + ' .glyphicon').removeClass("glyphicon-menu-up");
    $('#' + trigger_id + ' .glyphicon').addClass("glyphicon-menu-down");
});

$(".collapsable").on('shown.bs.collapse', function(event) {
    var trigger_id = $(event.target).attr("id").replace("_list", "_link");
    $('#' + trigger_id + ' .glyphicon').removeClass("glyphicon-menu-down");
    $('#' + trigger_id + ' .glyphicon').addClass("glyphicon-menu-up");
});