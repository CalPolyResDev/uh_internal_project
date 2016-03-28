from django.apps import AppConfig

from ....settings.base import MAIN_APP_NAME


class DatatablesTemplatetagsConfig(AppConfig):
    label = MAIN_APP_NAME + '.apps.datatables.templatetags'
    name = 'apps.datatables.templatetags'
