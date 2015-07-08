"""
.. module:: resnet_internal.apps.portmap.models
   :synopsis: ResNet Internal Residence Halls Port Map Models.

   Major credit to Kyle Fast for saving a couple months' worth of work entering database info.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>


"""

from django.db.models.base import Model
from django.db.models.fields import CharField, GenericIPAddressField, BooleanField, PositiveSmallIntegerField
from django.db.models.fields.related import ForeignKey

from ..core.models import Community, Building


class ResHallWired(Model):

    community = ForeignKey(Community, verbose_name='Community')
    building = ForeignKey(Building, verbose_name='Building')
    room = CharField(max_length=10, verbose_name='Room')
    switch_ip = GenericIPAddressField(protocol='IPv4', verbose_name='Switch IP')
    switch_name = CharField(max_length=35, verbose_name='Switch Name')
    jack = CharField(max_length=5, verbose_name='Jack')
    blade = PositiveSmallIntegerField(verbose_name='Blade')
    port = PositiveSmallIntegerField(verbose_name='Port')
    vlan = CharField(max_length=7, verbose_name='vLan')
    active = BooleanField(default=True, verbose_name='Active')

    def __str__(self):
        return str(self.community) + " - " + str(self.building) + " " + self.room + ": " + self.jack

    def save(self, *args, **kwargs):
        # Upper room and jack letters
        for field_name in ['room', 'jack']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())

        super(ResHallWired, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Residence Halls Wired Port'
