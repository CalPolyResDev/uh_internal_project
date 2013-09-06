"""
.. module:: resnet_internal.computers.models
   :synopsis: ResNet Internal Computer Index Models.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.db.models import Model, BooleanField, CharField, IntegerField, IPAddressField

from .fields import MACAddressField, ListField


class Computer(Model):
    """University Housing computers."""

    department = CharField(max_length=50, verbose_name=u'Department')
    sub_department = CharField(max_length=50, verbose_name=u'Sub Department')
    computer_name = CharField(max_length=25, verbose_name=u'Computer Name')
    ip_address = IPAddressField(verbose_name=u'IP Address')
    mac_address = MACAddressField(verbose_name=u'MAC Address')
    model = CharField(max_length=25, verbose_name=u'Model')
    serial_number = CharField(max_length=20, verbose_name=u'Serial Number')
    property_id = CharField(max_length=50, verbose_name=u'Cal Poly Property ID')
    dn = CharField(max_length=250, verbose_name=u'Distinguished Name')
    description = CharField(max_length=100, verbose_name=u'Description')

    def __unicode__(self):
        return self.computer_name

    class Meta:
        db_table = u'computers'
        managed = False
        verbose_name = u'University Housing Computer'


class Pinhole(Model):
    """University Housing Firewall Pinholes."""

    ip_address = IPAddressField(verbose_name=u'IP Address')
    service_name = CharField(max_length=50, verbose_name=u'Service Name')
    inner_fw = BooleanField(verbose_name=u'Inner Firewall')
    border_fw = BooleanField(verbose_name=u'Border Firewall')
    tcp_ports = ListField(verbose_name=u'TCP Ports')
    udp_ports = ListField(verbose_name=u'TCP Ports')
    sr_number = IntegerField(max_length=11, null=True, verbose_name=u'SR Number', db_column='ticket_id')

    def __unicode__(self):
        return 'Pinhole: ' + str(self.ip_address)

    class Meta:
        db_table = u'pinholes'
        managed = False
        verbose_name = u'University Housing Pinhole'


class DomainName(Model):
    """University Housing Domain Names."""

    ip_address = IPAddressField(verbose_name=u'IP Address')
    domain_name = CharField(max_length=100, verbose_name=u'Domain Name')
    sr_number = IntegerField(max_length=11, null=True, verbose_name=u'SR Number', db_column='ticket_id')

    def __unicode__(self):
        return 'DNS Record: ' + str(self.ip_address)

    class Meta:
        db_table = u'domain_names'
        managed = False
        verbose_name = u'University Housing Domain Name'
