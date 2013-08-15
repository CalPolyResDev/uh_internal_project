// Javascript to initialize the dataTable and commit changes to it
$(document).ready(function()
{
	// Initialize the DataTable. See datatables documentation for information about each option
	var csdMapTable = $('#csdMap').dataTable( {
		"oLanguage": {
			"sZeroRecords": "No records to display"
		},
		"bProcessing": true,
		"bServerSide": true,
		"sAjaxSource": "/admin/csdMap/get_records/",
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
					return "<span id='csdMapDomain_" + row.aData[0] + "'>" + row.aData[1] + "</span><input type='hidden' value='" + row.aData[1] +  "' id='csdMapDomain_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 1 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='csdMapName_" + row.aData[0] + "' class='text'>" + row.aData[2] + "</span><input type='text' value='" + row.aData[2] + "' class='editbox' style='width:146px' id='csdMapName_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 2 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='csdMapAlias_" + row.aData[0] + "' class='text'>" + row.aData[3] + "</span><input type='text' value='" + row.aData[3] + "' class='editbox' style='width:96px' id='csdMapAlias_input_" + row.aData[0] + "' /><input id='" + row.aData[0] + "' class='ref' type='hidden' />";
				},
				"aTargets": [ 3 ]
			},
		]
	});

	// Get information from a table row click
	$("#csdMap tbody tr td.editable_tr").live( 'click', function(event) {
		var rowPos = csdMapTable.fnGetPosition( event.target.parentNode );
		var rowData = csdMapTable.fnGetData( rowPos );
		var ID = rowData[0];

		// Hide text fields on edit click
		$("#csdMapName_"+ID).hide();
	    $("#csdMapAlias_"+ID).hide();

		// Show input fields on edit click
		$("#csdMapName_input_"+ID).show();
		$("#csdMapAlias_input_"+ID).show();

		// Use ajax to upload the data only after a field has changed
		$(".editbox").change(function() {
			var rowPos = csdMapTable.fnGetPosition( event.target.parentNode ).get();
			var rowData = csdMapTable.fnGetData( rowPos );
			var ID = rowData[0];

			// Grab editable field values from the table.
			var csdMapDomain=$("#csdMapDomain_input_"+ID).val();
			var csdMapName=$("#csdMapName_input_"+ID).val();
			var csdMapAlias=$("#csdMapAlias_input_"+ID).val();
			
			// Verify fields
			if (csdMapName.length > 0 && csdMapAlias.length > 0 && csdMapAlias.length < 9)
			{
				Dajaxice.resnet_internal.admin_userMap.update_table_csdMap(
					Dajax.process,{
						"pid": ID,
						"domain": csdMapDomain,
						"name": csdMapName,
						"alias": csdMapAlias,
					}
				);
			}
			else
			{
				if (csdMapAlias.length > 8)
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