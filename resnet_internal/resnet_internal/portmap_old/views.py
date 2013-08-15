from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
from resnet_internal.portMap.models import Halls
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
def portMap_test(user):
    if user.is_authenticated and (user.is_developer or user.is_staff or user.is_technician or user.is_net_admin):
        return True
    return False

@user_passes_test(portMap_test)
def render_table(request):
    return render_to_response('portMap/portMap.html', context_instance=RequestContext(request))

@user_passes_test(portMap_test)
def get_records(request):
    # The querySet of records to parse
    querySet = Halls.objects.all()

    # A dictionary map of each columns name and index
    columnMap = { 0: 'pid', 1 : 'community', 2: 'building', 3: 'room', 4: 'switch_ip', 5: 'jack', 6: 'blade', 7: 'port', 8: 'vlan' }

    # A list of searchable columns in the column map
    searchableColumns = ['community', 'building', 'room', 'switch_ip', 'jack', 'blade', 'port', 'vlan']

    recordParser = parse_records(request, querySet, columnMap, searchableColumns)
    jsonData = recordParser.get_json()

    return HttpResponse(jsonData, mimetype="application/javascript")
