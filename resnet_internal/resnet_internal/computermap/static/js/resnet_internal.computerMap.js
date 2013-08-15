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
	var computerMapTable = $('#computerMap').dataTable( {
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
			"sSearch": "Filter records:",
			"sZeroRecords": "No records to display"
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
			{ "sClass": "width100", "sType": "string", "aTargets": [] },
			{ "sClass": "width50", "sType": "string", "aTargets": [0] },
			{ "sClass": "editable_td width150", "sType": "ip-address", "aTargets": [4,6,8] },
			{ "sClass": "editable_td width50", "sType": "numeric", "aTargets": [1,2,3,5,7,9] },
			{ "sClass": "editable_tr width55", "sType": "numeric", "aTargets": [10] },
			{ "fnRender": function ( row ) {
					return "<span id='serialNumber_" + row.aData[0] + "'>" + row.aData[0] + "</span><input type='hidden' value='" + row.aData[0] +  "' id='serialNumber_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 0 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='department_" + row.aData[0] + "'>" + row.aData[1] + "</span><input type='hidden' value='" + row.aData[1] +  "' id='department_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 1 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='subDepartment_" + row.aData[0] + "'>" + row.aData[2] + "</span><input type='hidden' value='" + row.aData[2] +  "' id='subDepartment_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 3 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='computerName_" + row.aData[0] + "'>" + row.aData[3] + "</span><input type='hidden' value='" + row.aData[3] +  "' id='computerName_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 3 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='ipAddress_" + row.aData[0] + "' class='text'>" + row.aData[4] + "</span><input type='text' value='" + row.aData[4] + "' class='editbox' style='width:46px' id='ipAddress_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 4 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='macAddress_" + row.aData[0] + "' class='text'>" + row.aData[5] + "</span><input type='text' value='" + row.aData[5] + "' class='editbox' style='width:46px' id='macAddress_input_" + row.aData[0] + "' />";
				},
				"aTargets": [ 5 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='description_" + row.aData[0] + "' class='text'>" + row.aData[6] + "</span><input type='text' value='" + row.aData[6] + "' class='editbox' style='width:46px' id='description_input_" + row.aData[0] + "' /><input id='" + row.aData[0] + "' class='ref' type='hidden' />";
				},
				"aTargets": [ 6 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='model_" + row.aData[0] + "' class='text'>" + row.aData[7] + "</span><input type='text' value='" + row.aData[7] + "' class='editbox' style='width:46px' id='model_input_" + row.aData[0] + "' /><input id='" + row.aData[0] + "' class='ref' type='hidden' />";
				},
				"aTargets": [ 7 ]
			},
			{ "fnRender": function ( row ) {
					return "<span id='ouPath_" + row.aData[0] + "' class='text'>" + row.aData[8] + "</span><input type='text' value='" + row.aData[8] + "' class='editbox' style='width:46px' id='ouPath_input_" + row.aData[0] + "' /><input id='" + row.aData[0] + "' class='ref' type='hidden' />";
				},
				"aTargets": [ 8 ]
			},
			{ "fnRender": function ( row ) {
					var response = "<span id='configManStatus_" + row.aData[0] + "' class='text'>" + row.aData[9] + "</span><select class='editbox' style='width:46px' id='configManStatus_input_" + row.aData[0] + "'>";
					/*for (var i=0; i<{{configManStatus.length}}, i++)
					{
						response = response.concat("\n<option value=\'");
						response = response.concat({{configManStatus[i]}});
						response = response.conact("'</option>");
					}*/
					{% for choice in configManStatus %}
						{% if choice == row.aData[9] %}
							response = response.concat("\n<option selected=selected value='");
						{% else %}
							response = response.concat("\n<option value='");
						{% endif %}
						response = response.concat("{{ choice }}");
						response = response.conact("'</option>");
					{% endfor %}
					return response + "</select><input id='" + row.aData[0] + "' class='ref' type='hidden' />";
				},
				"aTargets": [ 9 ]
			},
			{ "fnRender": function ( row ) {
					return "<div id='grayBG' class='grayBox' style='display:none;'></div><div id='LightBox1' class='box_content' style='display:none;'>" + 
					"<table cellpadding='3' cellspacing='0' border='0'> <tr align='left'> <td colspan='2' bgcolor='#FFFFFF' style='padding:10px;'>" +
					"<div onclick='displayHideBox('1'); return false;' style='cursor:pointer;' align='right'>X</div>" +
					"<iframe src='{% url 'pinholePopup' %}" + row.aData[0] + "/'>Your browser does not support iFrames. Use a better one. ResNet Development is curious which browser you're using that doesn't support iFrames. Email us.</iframe>" +
					"</td></tr></table> </div> <span id='pinholeInfo_" + row.aData[0] + 
					"' class='text'><a href='#' onclick='displayHideBox('1'); return false;'>Show Pinhole Info</a>";
				},
				"aTargets": [ 10 ]
			},
		]
	});

	// Get information from a table row click
	$("#computerMap tbody tr td.editable_tr").live( 'click', function(event) {
		var rowPos = computerMapTable.fnGetPosition( event.target.parentNode );
		var rowData = computerMapTable.fnGetData( rowPos );
		var ID = rowData[0];

		// Hide text fields on edit click
		$("#department_"+ID).hide();
		$("#subDepartment_"+ID).hide();
	    $("#computerName_"+ID).hide();
	    $("#ipAddress_"+ID).hide();
	    $("#macAddress_"+ID).hide();
		$("#description_"+ID).hide();
	    $("#model_"+ID).hide();
	    $("#ouPath_"+ID).hide();
	    $("#configManStatus_"+ID).hide();

		// Show input fields on edit click
		$("#department_input_"+ID).show();
		$("#subDepartment_input_"+ID).show();
	    $("#computerName_input_"+ID).show();
	    $("#ipAddress_input_"+ID).show();
	    $("#macAddress_input_"+ID).show();
		$("#description_input_"+ID).show();
	    $("#model_input_"+ID).show();
	    $("#ouPath_input_"+ID).show();
	    $("#configManStatus_input_"+ID).show();

		// Use ajax to upload the data only after a field has changed
		$(".editbox").change(function() {
			var rowPos = computerMapTable.fnGetPosition( event.target.parentNode );
			var rowData = computerMapTable.fnGetData( rowPos );
			var ID = rowData[0];

			// Grab editable field values from the table.
			var department=$("#department_input_"+ID).val();
			var subDepartment=$("#subDepartment_input_"+ID).val();
			var computerName=$("#computerName_input_"+ID).val();
			var ipAddress=$("#ipAddress_input_"+ID).val();
			var macAddress=$("#macAddress_input_"+ID).val();
			var description=$("#description_input_"+ID).val();
			var model=$("#model_input_"+ID).val();
			var ouPath=$("#outPath_input_"+ID).val();
			var configManStatus=$("#configManStatus_input_"+ID).val();
			
			// Verify fields
			if (department.length > 0 && computerName.length > 0 && macAddress.length > 0 && description.length > 0 && model.length > 0 && ouPath.length > 0)
			{
				Dajaxice.resnet_internal.portMap.update_table(
					Dajax.process,{
						"serialNumber": ID,
						"department": department,
						"subDepartment": subDepartment,
						"computerName": computerName,
						"ipAddress": ipAddress,
						"macAddress": macAddress,
						"description": description,
						"model": model,
						"ouPath": ouPath,
						"configManStatus": configManStatus,
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