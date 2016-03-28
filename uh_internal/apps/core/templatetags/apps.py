from django.apps import AppConfig

from ....settings.base import MAIN_APP_NAME


class CoreTemplatetagsConfig(AppConfig):
    label = MAIN_APP_NAME + '.apps.core.templatetags'
    name = 'apps.core.templatetags'
