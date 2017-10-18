#!/usr/bin/python3

from .manage import activate_env

activate_env()

import django  # noqa
from django.core.handlers.wsgi import WSGIHandler  # noqa
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry  # noqa

django.setup()

# Import any functions with uWSGI decorators here:
from uh_internal.apps.network.tasks import update_slack_network_status  # noqa

application = Sentry(WSGIHandler())
