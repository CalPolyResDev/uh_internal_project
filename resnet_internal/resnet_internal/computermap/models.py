from django.db import models
import fields

#
# Resnet Internal computerMap models
#
# Author: Thomas Willson
# Email:  tewillso@calpoly.edu
#

#
# Computer Map
#
class Pinholes(models.Model):
    serviceName = models.CharField(max_length=50, verbose_name=u'Service Name')
    tcpPorts = models.CommaSeparatedIntegerField(max_length=50, verbose_name=u'TCP Ports')
    udpPorts = models.CommaSeparatedIntegerField(max_length=50, verbose_name=u'UDP Ports')
    
    ACTIVE = u'Active'
    INACTIVE = u'Inactive'
    DEPRECATED = u'Deprecated'
    statusChoices = (
                    (ACTIVE, u'Active'),
                    (INACTIVE, u'Inactive'),
                    (DEPRECATED, u'Deprecated'))
    status = models.CharField(max_length=10, choices=statusChoices, default=ACTIVE, verbose_name=u'Pinhole Status')

    
class Computer(models.Model):

    # These are the descriptions of the data in particular columns of the database table. Remember that
    # database table names are a concatenation of the app name and the model name, e.g.(appname_modelname)
    # Django will automatically add an Auto-Incrementing IntegerField to hold the primary key if none is
    # specified.
    serialNumber = models.CharField(max_length=50, primary_key=True, verbose_name=u'Serial Number')
    department = models.CharField(max_length=50, verbose_name=u'Department')
    subDepartment = models.CharField(max_length=50, verbose_name=u'Sub Department')
    computerName = models.CharField(max_length=25, verbose_name=u'Computer Name')
    ipAddress = models.IPAddressField()
    macAddress = fields.MACAddressField()
    description = models.CharField(max_length=100, verbose_name=u'Description')
    model = models.CharField(max_length=25, verbose_name=u'Model')
    ouPath = models.CharField(max_length=250, verbose_name=u'OU Path')
    
    UNKNOWN = u'Unknown'
    MANAGED = u'Managed'
    STAGED = u'Staged'
    configStatusChoices = (
                           (UNKNOWN, u'Unknown'),
                           (MANAGED, u'Managed'),
                           (STAGED, u'Staged'))
    configManStatus = models.CharField(max_length=10, choices=configStatusChoices, default=STAGED, verbose_name=u'Configuration Manager Status')
    pinholeInfo = models.ManyToManyField(Pinholes)



    