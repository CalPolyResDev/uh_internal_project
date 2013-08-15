from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import ensure_csrf_cookie
from models import CalHourA, CalDayA, Calendar, StudentCalendar, Tech
from django.contrib.auth.models import User
from resnet_internal.jCal import utils

#
# JCal Views
# These views control the display and modification of Jeannie's Calendar App
#
# Author: Chase Voorhees
# Email:  chase@cjvoorhees.com
#


def admin_makeCal(request, year, quarter, office, is_finals):
    #request.POST['lookup_type']
    pass



def admin_editCal(request):
    pass

def admin_viewAvail(request):
    pass





# given year, quarter, is_finals, office - return 2 dictionaries of hours containing techa(string name) and techb assignments for each 13*7 hours
def global_schedule(request, year, quarter, office, is_finals):
    if request.method == 'POST':
        currentCal = Calendar.objects.get(year=year, quarter=quarter, office=office, is_finals=is_finals)
        techDictA = dict()
        techDictB = dict()
        hCount = 0
        for CalDayA in currentCal.day:
            for CalHourA in CalDayA.hour:
                # TODO: Fix line below
                techDictA[hCount] = (Tech.objects.filter(_id=CalHourA.techA_id)).tName      #is this proper way to filter based on foreignkey?
                techDictB[hCount] = (Tech.objects.filter(_id=CalHourA.techB_id)).tName
                hCount += 1
        dataDict = dict()
        dataDict[0] = techDictA
        dataDict[1] = techDictB      
        return render_to_response('jCal/global.html', dataDict, context_instance = RequestContext(request))
    else:
        return HttpResponseForbidden()
    
# given year, quarter, is_finals, office, request.currentUser - returns a dictionary containing currentUser's tech assignments for each 13*7 hours
def my_schedule(request, year, quarter, office, is_finals):
    if request.method == 'POST':
        currentCal = Calendar.objects.get(year=year, quarter=quarter, office=office, is_finals=is_finals)
        dataDict = dict()
        hCount = 0
        for CalDayA in currentCal.day:
            for CalHourA in CalDayA.hour:
                #if the tech assigned is the currentUser then add them to the dictionary
                if (Tech.objects.filter(_id=CalHourA.techA_id)).tUser == request.user:
                    dataDict[hCount] = (Tech.objects.filter(_id=CalHourA.techA_id)).tName      
                if (Tech.objects.filter(_id=CalHourA.techB_id)).tUser == request.user:
                    dataDict[hCount] = (Tech.objects.filter(_id=CalHourA.techB_id)).tName      
                hCount += 1
        return render_to_response('jCal/personal.html', dataDict, context_instance = RequestContext(request))
    else:
        return HttpResponseForbidden()

def set_availability(request, year, quarter, office, is_finals):
    if request.method == 'POST':
        currentCal = StudentCalendar()
        #TODO fix lol
        currentCal.associatedTech = 'currentUser'
        currentCal.year = year
        currentCal.quarter = quarter
        currentCal.is_finals = is_finals
        currentCal.minHoursDesired = request.POST['minHoursDesired']
        currentCal.maxHoursDesired = request.POST['maxHoursDesired']
        
        #add hour data here - JSON string maybe?
        
        currentCal.save()
        
        #currentCal = StudentCalendar.objects.filter(year=request.POST['year']).filter(quarter=request.POST['quarter']).filter(is_finals=request.POST['is_finals']).filter(minHoursDesired=request.POST['minHoursDesired']).filter(maxHoursDesired=request.POST['maxHoursDesired'])
        #if currentCal == None:
            #make new calendar and assign it to currentCal
        #    currenctCal = StudentCalendar
        #else:
            #
        

#class StudentCalendar(models.Model):
#    associatedTech = models.ForeignKey(Tech)
#    day = [ CalDayA() for i in range(6)]
#    year = models.IntegerField()                             ##SET DEFAULT YEAR HERE??
#    quarter = models.CharField(max_length=2, choices = QUARTERS)
#    is_finals = models.BooleanField(default = False)    
#    minHoursDesired = models.IntegerField(default = 8)
#    maxHoursDesired = models.IntegerField(default = 12) 

#class Tech(models.Model):
#    tName = models.CharField(max_length=20)
#    tUser = models.OneToOneField(User)
#    tAssignPriority = models.IntegerField(default = 0)
#    tHourPriority = models.CharField(max_length=1, choices = PRIORITIES)
#    defaultShiftLength = models.IntegerField(default = 4)
#    minHours = models.IntegerField(default = 8)
#    maxHours = models.IntegerField(default = 12)
#    worksWith = models.ForeignKey(User)
        