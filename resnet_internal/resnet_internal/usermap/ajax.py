from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
#from resnet_internal.main.models import CSDMapping, StaffMapping

#
# resnet_internal Administration csdMap ajax methods
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

# @dajaxice_register
# def update_table_csdMap(request, pid, domain, name, alias):
#     dajax = Dajax()
# 
#     # Add a temporary loading image to the edited row
#     dajax.assign('#domain_' + str(pid), 'innerHTML', '<img src="/static/images/datatables/load.gif" />')
# 
#     # Update the database entries
#     CSDMappingInstance = CSDMapping.objects.get(id=pid)
#     CSDMappingInstance.csd_name = name
#     CSDMappingInstance.csd_alias = alias
#     CSDMappingInstance.save()
# 
#     # Update the table
#     dajax.assign('#domain_' + str(pid), 'innerHTML', domain)  # Overwrites the loading image with the data
#     dajax.assign('#name_' + str(pid), 'innerHTML', name)
#     dajax.assign('#alias_' + str(pid), 'innerHTML', alias)
# 
#     return dajax.json()
# 
# @dajaxice_register
# def update_table_StaffMap(request, pid, title, name, alias):
#     dajax = Dajax()
# 
#     # Add a temporary loading image to the edited row
#     dajax.assign('#title_' + str(pid), 'innerHTML', '<img src="/static/images/datatables/load.gif" />')
# 
#     # Update the database entries
#     StaffMappingInstance = StaffMapping.objects.get(id=pid)
#     StaffMappingInstance.staff_title = title
#     StaffMappingInstance.staff_name = name
#     StaffMappingInstance.staff_alias = alias
#     StaffMappingInstance.save()
# 
#     # Update the table
#     dajax.assign('#title_' + str(pid), 'innerHTML', title)  # Overwrites the loading image with the data
#     dajax.assign('#name_' + str(pid), 'innerHTML', name)
#     dajax.assign('#alias_' + str(pid), 'innerHTML', alias)
# 
#     return dajax.json()

