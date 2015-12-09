"""
.. module:: reslife_internal.apps.rosters.views
   :synopsis: ResLife Internal Roster Generator Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from clever_selects.views import ChainedSelectFormViewMixin
import csv
from operator import itemgetter

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.generic.edit import FormView
from rmsconnector.constants import SIERRA_MADRE, YOSEMITE, CERRO_VISTA, POLY_CANYON_VILLAGE, POLY_CANYON_VILLAGE_BUILDINGS
from rmsconnector.utils import reverse_address_lookup

from .forms import GenerationForm, AddressRangeSearchForm
from .utils import room_list_generator


MIN_ROOM = 'A'
MAX_ROOM = 'R'


class BaseGenerateView(FormView):
    """Generates an HTML table or CSV file containing student information based on form input."""

    attribute_list = ["full_name", "sex", "address", "cell_phone", "dorm_phone", "college", "major", "course_year", "email", "is_buckley"]
    empty_error_message_csv = "The addresses provided do not match University Housing records or are currently vacant."
    empty_error_message_html = "The addresses provided do not match University Housing records or are currently vacant."

    @cache_control(no_cache=True, must_revalidate=True, no_store=True)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseGenerateView, self).dispatch(request, *args, **kwargs)

    def get_content_disposition(self):
        raise NotImplementedError("Please provide a content_disposition.")

    def render_to_response(self, context, **response_kwargs):
        if context['form'].is_valid() and self.request.POST['mode'] == "csv":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = self.get_content_disposition(context)

            writer = csv.writer(response, dialect='excel', delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writerow(["Name", "Dorm Address", "Cell Phone", "Dorm Phone", "E-mail Address", "Buckley Status", "Picture?", "Signature"])
            for row in context["resident_list"]:
                writer.writerow(row)
            else:
                writer.writerow([self.empty_error_message_csv])

            return response
        else:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(request=self.request, template=self.get_template_names(), context=context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseGenerateView, self).get_context_data(**kwargs)

        if self.request.method == "POST":
            resident_data = []

            for resident in kwargs.pop('resident_list', []):
                if self.request.POST['mode'] == "csv":
                    resident_data.append([getattr(resident, attribute) for attribute in self.attribute_list])
                    resident_data.sort(key=itemgetter(2))
                else:
                    resident_data.append({attribute: getattr(resident, attribute) for attribute in self.attribute_list})
                    resident_data.sort(key=itemgetter('address'))
            else:
                context['error_message'] = self.empty_error_message_html

            context['resident_data'] = resident_data

        return context


class FDGenerateView(ChainedSelectFormViewMixin, BaseGenerateView):

    template_name = 'rosters/fd_roster.html'
    report_template_name = 'rosters/fd_roster_report.html'
    form_class = AddressRangeSearchForm

    def get_content_disposition(self, context):
        return "attachment; filename=FDRoster_%(community)s_%(building)s_Rooms_%(start_room)s-%(end_room)s.csv" % {'community': context["community"].replace(" ", "_"), 'building': context["building"].replace(" ", "_"), 'start_room': context["start_room"].replace(" ", "_"), 'end_room': context["end_room"].replace(" ", "_")}

    def form_valid(self, form):
        self.template_name = self.report_template_name

        community = form.cleaned_data['community'].name
        building = form.cleaned_data['building'].name
        start_room = form.cleaned_data['start_room']
        end_room = form.cleaned_data['end_room']

        # Create a list of rooms based on a room range
        room_list = []

        if community == SIERRA_MADRE or community == YOSEMITE:
            room_list = room_list_generator(start_room, end_room)
        else:
            start = int(''.join([x for x in start_room if x.isdigit()]))
            end = int(''.join([x for x in end_room if x.isdigit()]))

            room_list = range(start, end + 1)

        resident_list = []

        for room in room_list:
            try:
                resident_list.extend(reverse_address_lookup(community, building, room))
            except ObjectDoesNotExist:
                pass

        return self.render_to_response(self.get_context_data(form=form,
                                                             community=community,
                                                             building=building,
                                                             start_room=start_room,
                                                             end_room=end_room,
                                                             resident_list=resident_list))


class CSDGenerateView(BaseGenerateView):

    template_name = 'rosters/csd_roster.html'
    report_template_name = 'rosters/csd_roster_report.html'
    form_class = GenerationForm

    empty_error_message_csv = "No one currently lives in this residence hall."
    empty_error_message_html = "No one currently lives in this residence hall."

    def get_content_disposition(self, context):
        return "attachment; filename=CSDRoster_%(hall)s.csv" % {'hall': context["hall"].replace(" ", "_")}

    def form_valid(self, form):
        self.template_name = self.report_template_name

        hall = form.cleaned_data['hall']

        resident_list = []

        try:
            # Gather records from hall requests
            if hall == SIERRA_MADRE or hall == YOSEMITE or hall == CERRO_VISTA:
                resident_list = reverse_address_lookup(community=hall)
            elif hall == "Santa Lucia":
                resident_list = reverse_address_lookup(building=hall)
                resident_list.extend(reverse_address_lookup(community="North Mountain"))
            elif hall.startswith(POLY_CANYON_VILLAGE):
                raw_resident_list = reverse_address_lookup(community=POLY_CANYON_VILLAGE)

                if hall == POLY_CANYON_VILLAGE + " 1":
                    buildings = POLY_CANYON_VILLAGE_BUILDINGS[0:2]
                elif hall == POLY_CANYON_VILLAGE + " 2":
                    buildings = POLY_CANYON_VILLAGE_BUILDINGS[3:5]
                elif hall == POLY_CANYON_VILLAGE + " 3":
                    buildings = POLY_CANYON_VILLAGE_BUILDINGS[6:8]
                else:
                    buildings = []

                resident_list = [resident for resident in raw_resident_list if resident.address_dict["building"] in [buildings]]
            else:
                resident_list = reverse_address_lookup(building=hall)
        except ObjectDoesNotExist:
            pass

        return self.render_to_response(self.get_context_data(form=form,
                                                             resident_list=resident_list,
                                                             hall=hall))
