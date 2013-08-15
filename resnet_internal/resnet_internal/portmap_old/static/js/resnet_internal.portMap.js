//IP Address Filter for dataTables
jQuery.fn.dataTableExt.aTypes.unshift(
    function ( sData )
    {
        if (/^\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b$/.test(sData)) {
            return 'ip-address';
        }
        return null;
    }
);

// Javascript to initialize the dataTable and commit changes to it
$(document).ready(function()
{
	// Initialize the DataTable. See datatables documentation for information about each option
	var resHallPortsTable = $('#resHallPorts').dataTable( {
		"aaSorting": [[ 1, "asc" ], [ 2, "asc" ], [ 3, "asc" ]],
		"oLanguage": {
			"sLengthMenu": 'Display <select>'+
				'<option value="50">50</option>'+
				'<option value="100">100</option>'+
				'<option value="250">250</option>'+
				'<option value="500">500</option>'+
				'<option value="1000">1000</option>'+
				'<option value="-1">All</option>'+
				'</select> records:',
			"sSearch": "Filter records (use ?<i>username</i> to search RMS):",
			"sZeroRecords": "No records to display."
		},
		"bProcessing": true,
		"bServerSide": true,
		"sAjaxSource": "/portMap/get_records/",
		"iDisplayLength": 50,
		"sPaginationType": "full_numbers",
		"bLengthChange": true,
		"bAutoWidth": false,
		"sDom": '<lrf><"clear">t<ip><"clear">',
		// Custom column rendering
		"aoColumnDefs": [
			{ "sClass": "width0","bSearchable": false, "bVisible": false, "aTargets": [ 0 ] },
			{ "sClass": "width100", "sType": "string", "aTargets": [ 1, 2 ] },
			{ "sClass": "width50", "sType": "string", "aTargets": [ 3, 5 ] },
			{ "sClass": "editable_td width150", "sType": "ip-address", "aTargets": [ 4 ] },
			{ "sClass": "editable_td width50", "sType": "numeric", "aTargets": [ 6, 7 ] },
			{ "sClass": "editable_td  editable_tr width55", "sType": "numeric", "aTargets": [ 8 ] },
			{ "fnRender": function ( row ) {
					return "<span id='community_" + row.aData[0] + "'>" + row.aData[1] + "</span><input type='hidden' value='" + row.aData[1] +  "' id='community_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 1 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='building_" + row.aData[0] + "'>" + row.aData[2] + "</span><input type='hidden' value='" + row.aData[2] +  "' id='building_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 2 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='room_" + row.aData[0] + "'>" + row.aData[3] + "</span><input type='hidden' value='" + row.aData[3] +  "' id='room_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 3 ]
			},
			{ "fnRender": function ( row ) {
					return "<a href='/frame/cisco/" + row.aData[4] + "/' target='_blank'><span id='switch_ip_" + row.aData[0] + "' class='text'>" + row.aData[4] + "</span></a><input type='text' value='" + row.aData[4] + "' class='editbox' style='width:146px' id='switch_ip_input_" + row.aData[0] + "' /><img id='switch_img_" + row.aData[0] + "' class='switchImg' src='/static/images/icons/cisco.gif' style='padding-left:5px;' align='top' width='16' height='16' border='0' />";
				},
				"aTargets": [ 4 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='jack_" + row.aData[0] + "'>" + row.aData[5] + "</span><input type='hidden' value='" + row.aData[5] +  "' id='jack_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 5 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='blade_" + row.aData[0] + "' class='text'>" + row.aData[6] + "</span><input type='text' value='" + row.aData[6] + "' class='editbox' style='width:46px' id='blade_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 6 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='port_" + row.aData[0] + "' class='text'>" + row.aData[7] + "</span><input type='text' value='" + row.aData[7] + "' class='editbox' style='width:46px' id='port_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 7 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='vlan_" + row.aData[0] + "' class='text'>" + row.aData[8] + "</span><input type='text' value='" + row.aData[8] + "' class='editbox' style='width:46px' id='vlan_input_" + row.aData[0] + "' /><input id='" + row.aData[0] + "' class='ref' type='hidden' />";
				},
				"aTargets": [ 8 ]
			},
		]
	});

	// Get information from a table row click
	$("#resHallPorts tbody tr td.editable_tr").live( 'click', function(event) {
		var rowPos = resHallPortsTable.fnGetPosition( event.target.parentNode );
		var rowData = resHallPortsTable.fnGetData( rowPos );
		var ID = rowData[0];

		// Hide text fields on edit click
		$("#switch_ip_"+ID).hide();
		$("#switch_img_"+ID).hide();
		$("#blade_"+ID).hide();
	    $("#port_"+ID).hide();
	    $("#vlan_"+ID).hide();

		// Show input fields on edit click
		$("#switch_ip_input_"+ID).show();
		$("#blade_input_"+ID).show();
		$("#port_input_"+ID).show();
		$("#vlan_input_"+ID).show();

		// Use ajax to upload the data only after a field has changed
		$(".editbox").change(function() {
			var rowPos = resHallPortsTable.fnGetPosition( event.target.parentNode );
			var rowData = resHallPortsTable.fnGetData( rowPos );
			var ID = rowData[0];

			// Grab editable field values from the table.
			var community=$("#community_input_"+ID).val();
			var switch_ip=$("#switch_ip_input_"+ID).val();
			var blade=$("#blade_input_"+ID).val();
			var port=$("#port_input_"+ID).val();
			var vlan=$("#vlan_input_"+ID).val();

			// Verify fields
			if (switch_ip.length > 0 && blade.length > 0 && port.length > 0 && vlan.length > 0)
			{
				Dajaxice.resnet_internal.portMap.update_table(
					Dajax.process,{
						"pid": ID,
						"community": community,
						"switch_ip": switch_ip,
						"blade": blade,
						"port": port,
						"vlan": vlan,
					}
				);
			}
			else
			{
				alert('Please fill all editable fields with data.');
			}
		});

		// Edit input box click action
		$(".editbox").mouseup(function() {
			return false
		});

		// Outside click action
		$(document).mouseup(function() {
			$(".editbox").hide();
			$(".text").show();
			$(".switchImg").show();
		});
	});
});