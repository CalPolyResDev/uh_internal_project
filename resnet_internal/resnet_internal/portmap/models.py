"""
.. module:: resnet_internal.portmap.models
   :synopsis: ResNet Internal Residence Halls Port Map Models.

   Major credit to Kyle Fast for saving a couple months' worth of work entering database info.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>


"""

from django.db.models import Model, CharField, IPAddressField, BooleanField


class ResHallWired(Model):

    community = CharField(max_length=25, verbose_name=u'Community')
    building = CharField(max_length=25, verbose_name=u'Building')
    room = CharField(max_length=10, verbose_name=u'Room')
    switch_ip = IPAddressField(verbose_name=u'Switch IP')
    switch_name = CharField(max_length=35, verbose_name=u'Switch Name')
    jack = CharField(max_length=5, verbose_name=u'Jack')
    blade = CharField(max_length=2, verbose_name=u'Blade')
    port = CharField(max_length=2, verbose_name=u'Port')
    vlan = CharField(max_length=7, verbose_name=u'vLan')
    active = BooleanField(default=True, verbose_name=u'Active')

    def __unicode__(self):
        return self.community + " - " + self.building + " " + self.room + ": " + self.jack

    class Meta:
        db_table = u'residence_halls_wired'
        managed = False
        verbose_name = u'Residence Halls Wired Port'
