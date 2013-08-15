from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from resnet_internal.portMap.models import Halls

#
# resnet_internal portmap ajax methods
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#

@dajaxice_register
def update_table(request, pid, community, switch_ip, blade, port, vlan):
    dajax = Dajax()

    # Add a temporary loading image to the edited row
    dajax.assign('#community_' + pid, 'innerHTML', '<img src="/static/images/datatables/load.gif" />')

    # Update the database entries
    HallsInstance = Halls.objects.get(pid=pid)
    HallsInstance.switch_ip = switch_ip
    HallsInstance.blade = blade
    HallsInstance.port = port
    HallsInstance.vlan = vlan
    HallsInstance.save()

    # Update the table
    dajax.assign('#community_' + pid, 'innerHTML', community) # Overwrites the loading image with the data
    dajax.assign('#switch_ip_' + pid, 'innerHTML', switch_ip)
    dajax.assign('#blade_' + pid, 'innerHTML', blade)
    dajax.assign('#port_' + pid, 'innerHTML', port)
    dajax.assign('#vlan_' + pid, 'innerHTML', vlan)

    return dajax.json()


