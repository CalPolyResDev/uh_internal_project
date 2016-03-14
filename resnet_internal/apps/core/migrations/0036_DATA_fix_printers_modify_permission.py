from __future__ import unicode_literals

from django.db import migrations
from ....settings.base import PRINTERS_MODIFY_ACCESS


def fix_permission_class(apps, schema_editor):
    """``UH TAG Member (Read-only)`` should not have PRINTERS_MODIFY_ACCESS."""

    permission_name = PRINTERS_MODIFY_ACCESS
    group_display_name = 'UH TAG Member (Read-only)'

    PermissionClass = apps.get_model('core', 'PermissionClass')
    ADGroup = apps.get_model('core', 'ADGroup')

    if PermissionClass.objects.filter(name=permission_name).exists():
        permission_class = PermissionClass.objects.get(name=permission_name)

        try:
            ad_group = ADGroup.objects.get(display_name=group_display_name)
        except ADGroup.DoesNotExist:
            pass
        else:
            permission_class.groups.remove(ad_group)

        permission_class.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_DATA_add_infrastructure_device_link'),
    ]

    operations = [
        migrations.RunPython(fix_permission_class),
    ]
