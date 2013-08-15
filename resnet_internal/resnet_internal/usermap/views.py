from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
# from resnet_internal.main.models import CSDMapping, StaffMapping
from utils import parse_records
from django.contrib.auth.decorators import user_passes_test

#
# csdMap Views
# These views output the display of a dynamic, editable table.
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

#
# Permissions Test
#
def userMap_test(user):
    if user.is_authenticated and user.is_developer:
        return True
    return False
# 
# @user_passes_test(userMap_test)
# def render_table(request):
#     return render_to_response('admin/userMap.html', context_instance=RequestContext(request))
# 
# @user_passes_test(userMap_test)
# def get_records_csdMap(request):
#     # The querySet of records to parse
#     querySet = CSDMapping.objects.all()
# 
#     # A dictionary map of each columns name and index
#     columnMap = { 0: 'id', 1 : 'csd_domain', 2: 'csd_name', 3: 'csd_alias' }
# 
#     # A list of searchable columns in the column map
#     searchableColumns = ['csd_domain', 'csd_name', 'csd_alias']
# 
#     recordParser = parse_records(request, querySet, columnMap, searchableColumns)
#     jsonData = recordParser.get_json()
# 
#     return HttpResponse(jsonData, mimetype="application/javascript")
# 
# @user_passes_test(userMap_test)
# def get_records_staffMap(request):
#     # The querySet of records to parse
#     querySet = StaffMapping.objects.all()
# 
#     # A dictionary map of each columns name and index
#     columnMap = { 0: 'id', 1 : 'staff_title', 2: 'staff_name', 3: 'staff_alias', 4: 'staff_ext'}
# 
#     # A list of searchable columns in the column map
#     searchableColumns = ['staff_domain', 'staff_name', 'staff_alias', 'staff_ext']
# 
#     recordParser = parse_records(request, querySet, columnMap, searchableColumns)
#     jsonData = recordParser.get_json()
# 
#     return HttpResponse(jsonData, mimetype="application/javascript")

