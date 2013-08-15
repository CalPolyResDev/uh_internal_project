from django.db import models

#
# Judicial Management Application Models
# These models supply the data for a dynamic, editable table used for a Port Map in this instance.
#
# Author: Alex Kavanaugh
# Email:  kavanaugh.development@outlook.com
#
# First, a little overview on how Django interfaces with a database:
#
# Source "http://www.djangobook.com/en/2.0/chapter05/"
#
# "A Django model is a description of the data in your database, represented as Python code.
#  It's your data layout - the equivalent of your SQL CREATE TABLE statements - except it's
#  in Python instead of SQL, and it includes more than just database column definitions.
#  Django uses a model to execute SQL code behind the scenes and return convenient Python data
#  structures representing the rows in your database tables. Django also uses models to represent
#  higher-level concepts that SQL can't necessarily handle."
#
# Basically, this is where the data in your database is defined. The name of the database table is
# concatenated like so: "appname_modelname".
#
# The models explicity describes the date in the database. This way, accurate and complete information
# is stored, in Python, and the overhead of runtime database introspection is eliminated. It requires
# a bit more work on the development end, but the app's efficiency improves drastically.
#
# The 'using' command tells the model which database connection to use. See 
# https://docs.djangoproject.com/en/dev/topics/db/multi-db/#manually-selecting-a-database-for-a-queryset
# for more details.
#
# ex: Logs.objects.using('cisco_logs').all()
# This returns all Logs using the 'cisco_logs' database.
#


#
# Log Data for the Judicial Management Application. This is the raw data coming from the CCA Logs.
#
class Logs(models.Model):

#  
# The Meta Class changes the way the model behaves. Since this model uses a database that is external
# from the Django app, we are declaring the name of the existing table and disallowing Django to manage
# the table/database.
#
# For more information on the different Meta Class options, visit "https://docs.djangoproject.com/en/dev/ref/models/options/"
# 
    class Meta:
        db_table = 'kiwi_syslog'
        managed = False
        # Set default datetime field
        get_latest_by = "log_datetime"

# These are the descriptions of the data in particular columns of the database table. Remember that
# database table names are a concatenation of the app name and the model name, e.g.(appname_modelname)
# Django will automatically add an Auto-Incrementing IntegerField to hold the primary key if none is
# specified.
    lid = models.IntegerField(max_length=10, primary_key=True)
    log_datetime = models.DateTimeField(max_length=19, verbose_name=u'Date/Time')
    log_details = models.TextField(max_length=1024, verbose_name=u'Details')

# Provides a human-readable representation of an object. In this case, the id of each object is returned.
    def __unicode__(self):
        return self.log_details

##
## Infringment Data for the Judicial Management Application. This is a collection of infringements.
## TODO: Find a structure for this data... 
##
#class Infringements(models.Model):
#    
## These are the descriptions of the data in particular columns of the database table. Remember that
## database table names are a concatenation of the app name and the model name, e.g.(appname_modelname)
## Django will automatically add an Auto-Incrementing IntegerField to hold the primary key if none is
## specified.
#
#
## Provides a human-readable representation of an object. In this case, the id of each object is returned.
#    def __unicode__(self):
#        return self.id
