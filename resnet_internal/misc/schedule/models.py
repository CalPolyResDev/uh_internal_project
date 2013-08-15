from django.db import models
from django.contrib.auth.models import User

#
# And so the holy tablets of documentation were given unto this world by the 
# great SysAdmin Alex, and the world rejoiced for finally his Great Insight
# might be passed down for the betterment many generations of CP IT techs.
# 
# JCal Models
#
# Author: Chase Voorhees
# Email:  chase@cjvoorhees.com
#

#named as such due to weird interference from datetime (CalHour did not work)
class CalHourA(models.Model):
    ##this is still just referencing Tech, but it's a circular ForeignKey so we force it resolve it on compile by using a string
    techA = models.ForeignKey('Tech', null=True, blank=True, related_name='Tech', default=None)
    techB = models.ForeignKey('Tech', null=True, blank=True, related_name='Tech', default=None)
    def __init__(self, techA=None, techB=None):
        self.techA = techA
        self.techB = techB


#named as such to be consistent with CalHourA
class CalDayA(models.Model):
    #9am - 10pm = 13 hours
    hour = [CalHourA() for i in range(13)]

QUARTERS = (
               ('fa', 'Fall'),
               ('wi', 'Winter'),
               ('sp', 'Spring'),
               ('su', 'Summer'),
)

PRIORITIES = (
            ('l', 'Low'),
            ('m', 'Medium'),
            ('h', 'High'),
)

#### Update to django 1.5
class Tech(models.Model):
    tName = models.CharField(max_length=20)
    tUser = models.OneToOneField(User)
    tAssignPriority = models.IntegerField(default=0)        #which order you are assigned in. Lower numbers = working towards beginning of week.
    tHourPriority = models.CharField(max_length=1, choices=PRIORITIES)    #low/med/high - this may be deprecated
    defaultShiftLength = models.IntegerField(default=4)
    minHours = models.IntegerField(default=8)
    maxHours = models.IntegerField(default=12)
    worksWith = models.ForeignKey(User)

class StudentCalendar(models.Model):
    associatedTech = models.ForeignKey(Tech)
    day = [ CalDayA() for i in range(7)]
    year = models.IntegerField()                             ##SET DEFAULT YEAR HERE??
    quarter = models.CharField(max_length=2, choices=QUARTERS)
    is_finals = models.BooleanField(default=False)
    minHoursDesired = models.IntegerField(default=8)
    maxHoursDesired = models.IntegerField(default=12)

OFFICES = (
            ('sm', 'Sierra Madre'),
            ('pc', 'Poly Canyon Village'),
)

class Calendar(models.Model):
    day = [CalDayA() for i in range(6)]
    year = models.IntegerField()                            ##SET DEFAULT YEAR HERE??
    quarter = models.CharField(max_length=2, choices=QUARTERS)
    office = models.CharField(max_length=3, choices=OFFICES)
    is_finals = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)             ##DEPENDING ON How we archive these things this may not be necessary
    under_construction = models.BooleanField(default=True)



# Provides a human-readable representation of an object. In this case, the name associated with the package is returned
    def __unicode__(self):
        return self.Name
