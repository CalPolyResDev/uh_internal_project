from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
from models import Computer
from utils import parse_records
from django.contrib.auth.decorators import user_passes_test

#
# Port Map Views
# These views output the display of a dynamic, editable table used for a Port Map in this instance.
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

#
# Permissions Test
#
def computerMap_test(user):
    if user.is_authenticated and (user.is_developer or user.is_staff or user.is_technician or user.is_net_admin):
        return True
    return False

@user_passes_test(computerMap_test)
def render_table(request):
    return render_to_response('computerList/computerList.html', {"configStatusChoices": Computer.configStatusChoices}, context_instance=RequestContext(request))

#@user_passes_test(computerMap_test)
#def view_pinholes(request):
#    return render_to_response('computerList/pinholes.html')

@user_passes_test(computerMap_test)
def get_records(request):
    # The querySet of records to parse
    querySet = Computer.objects.all()

    # A dictionary map of each columns name and index
    columnMap = { 0: 'serialNumber', 1 : 'department', 2: 'subDepartment', 3: 'computerName', 4: 'ipAddress', 5: 'macAddress', 6: 'description', 7: 'model', 8: 'ouPath', 9: 'configManStatus', 10: 'pinholeInfo'}

    # A list of searchable columns in the column map
    searchableColumns = ['serialNumber', 'department', 'subDepartment', 'computerName', 'ipAddress', 'macAddress', 'description', 'model', 'ouPath', 'configManStatus']

    recordParser = parse_records(request, querySet, columnMap, searchableColumns)
    jsonData = recordParser.get_json()

    return HttpResponse(jsonData, mimetype="application/javascript")
