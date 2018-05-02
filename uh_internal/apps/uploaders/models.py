"""
.. module:: resnet_internal.apps.uploaders.models
   :synopsis: University Housing Internal Uploaders Models.

.. moduleauthor:: Kyle Reis <FedoraReis@gmail.com>

"""

from django.db.models import Model
from django.db.models.fields import CharField, DateTimeField, BooleanField


class Uploaders(Model):
    """Uploader Information"""

    name = CharField(max_length=15, verbose_name='Uploader Name')
    last_run = DateTimeField(verbose_name='Last DateTime run')
    successful = BooleanField(verbose_name='If the run was successful')

    class Meta(object):
        verbose_name_plural = 'Uploaders'
        verbose_name = 'Uploader'
