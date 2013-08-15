// Javascript to initialize the dataTable and commit changes to it
$(document).ready(function()
{
	// Initialize the DataTable. See datatables documentation for information about each option
	var rnStaffMapTable = $('#rnStaffMap').dataTable( {
		"oLanguage": {
			"sZeroRecords": "No records to display"
		},
		"bProcessing": true,
		"bServerSide": true,
		"sAjaxSource": "/admin/staffMap/get_records/",
		"iDisplayLength": 15,
		"sPaginationType": "full_numbers",
		"bLengthChange": true,
		"bAutoWidth": false,
		"sDom": '<r><"clear">t<"clear">',
		// Custom column rendering
		"aoColumnDefs": [
			{ "sClass": "width0","bSearchable": false, "bVisible": false, "aTargets": [ 0 ] },
			{ "sClass": "width200", "sType": "string", "aTargets": [ 1 ] },
			{ "sClass": "editable_td width150", "sType": "string", "aTargets": [ 2 ] },
			{ "sClass": "editable_td editable_tr width100", "sType": "string", "aTargets": [ 3 ] },
			{ "fnRender": function ( row ) {
					return "<span id='rnStaffMapTitle_" + row.aData[0] + "'>" + row.aData[1] + "</span><input type='hidden' value='" + row.aData[1] +  "' id='rnStaffMapTitle_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 1 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='rnStaffMapName_" + row.aData[0] + "' class='text'>" + row.aData[2] + "</span><input type='text' value='" + row.aData[2] + "' class='editbox' style='width:146px' id='rnStaffMapName_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 2 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='rnStaffMapAlias_" + row.aData[0] + "' class='text'>" + row.aData[3] + "</span><input type='text' value='" + row.aData[3] + "' class='editbox' style='width:96px' id='rnStaffMapAlias_input_" + row.aData[0] + "' /><input id='" + row.aData[0] + "' class='ref' type='hidden' />";
				},
				"aTargets": [ 3 ]
			},
		]
	});

	// Get information from a table row click
	$("#rnStaffMap tbody tr td.editable_tr").live( 'click', function(event) {
		var rowPos = rnStaffMapTable.fnGetPosition( event.target.parentNode );
		var rowData = rnStaffMapTable.fnGetData( rowPos );
		var ID = rowData[0];

		// Hide text fields on edit click
		$("#rnStaffMapName_"+ID).hide();
	    $("#rnStaffMapAlias_"+ID).hide();

		// Show input fields on edit click
		$("#rnStaffMapName_input_"+ID).show();
		$("#rnStaffMapAlias_input_"+ID).show();

		// Use ajax to upload the data only after a field has changed
		$(".editbox").change(function() {
			var rowPos = rnStaffMapTable.fnGetPosition( event.target.parentNode ).get();
			var rowData = rnStaffMapTable.fnGetData( rowPos );
			var ID = rowData[0];

			// Grab editable field values from the table.
			var rnStaffMapTitle=$("#rnStaffMapTitle_input_"+ID).val();
			var rnStaffMapName=$("#rnStaffMapName_input_"+ID).val();
			var rnStaffMapAlias=$("#rnStaffMapAlias_input_"+ID).val();
			
			// Verify fields
			if (rnStaffMapName.length > 0 && rnStaffMapAlias.length > 0 && rnStaffMapAlias.length < 9)
			{
				Dajaxice.resnet_internal.admin_userMap.update_table_rnStaffMap(
					Dajax.process,{
						"pid": ID,
						"title": rnStaffMapTitle,
						"name": rnStaffMapName,
						"alias": rnStaffMapAlias,
					}
				);
			}
			else
			{
				if (rnStaffMapAlias.length > 8)
				{
					alert("The alias provided is longer than eight characters.")
				}
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
		});
	});
});