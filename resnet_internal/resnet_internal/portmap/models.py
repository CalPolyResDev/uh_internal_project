"""
.. module:: resnet_internal.portmap.models
   :synopsis: ResNet Internal Residence Halls Port Map Models.

   Major credit to Kyle Fast for saving a couple months' worth of work entering database info.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>


"""

from django.db.models import Model, CharField, GenericIPAddressField, BooleanField, PositiveSmallIntegerField
from rmsconnector.constants import COMMUNITIES, ALL_BUILDINGS


class ResHallWired(Model):
    COMMUNITY_CHOICES = [(community, community) for community in COMMUNITIES]
    BUILDING_CHOICES = [(building, building) for building in ALL_BUILDINGS]

    community = CharField(max_length=25, verbose_name='Community', choices=COMMUNITY_CHOICES)
    building = CharField(max_length=25, verbose_name='Building', choices=BUILDING_CHOICES)
    room = CharField(max_length=10, verbose_name='Room')
    switch_ip = GenericIPAddressField(protocol='IPv4', verbose_name='Switch IP')
    switch_name = CharField(max_length=35, verbose_name='Switch Name')
    jack = CharField(max_length=5, verbose_name='Jack')
    blade = PositiveSmallIntegerField(verbose_name='Blade')
    port = PositiveSmallIntegerField(verbose_name='Port')
    vlan = CharField(max_length=7, verbose_name='vLan')
    active = BooleanField(default=True, verbose_name='Active')

    def __str__(self):
        return self.community + " - " + self.building + " " + self.room + ": " + self.jack

    def save(self, *args, **kwargs):
        # Upper room and jack letters
        for field_name in ['room', 'jack']:
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, value.upper())

        # Replace spaces in towers with underscores
        value = getattr(self, 'building', None)
        if value and "Tower " in value:
            setattr(self, 'building', value.replace("Tower ", "Tower_"))

        super(ResHallWired, self).save(*args, **kwargs)

    class Meta:
        db_table = 'residence_halls_wired'
        managed = False
        verbose_name = 'Residence Halls Wired Port'
