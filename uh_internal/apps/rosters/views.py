"""
.. module:: resnet_internal.apps.rosters.views
   :synopsis: University Housing Internal Roster Generator Views.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

import csv
from operator import itemgetter

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.generic.edit import FormView

from rmsconnector.utils import reverse_address_lookup

from .forms import GenerationForm


class RosterGenerateView(FormView):
    """Generates an HTML table or CSV file containing student information based on form input."""

    form_class = GenerationForm
    template_name = 'rosters/rosters.djhtml'
    report_template_name = 'rosters/rosters_report.djhtml'

    attribute_list = ["full_name", "sex", "address", "cell_phone", "dorm_phone", "college", "major", "course_year", "email", "is_buckley"]
    empty_error_message_csv = "The buildings provided are currently vacant."
    empty_error_message_html = "The buildings provided are currently vacant."

    @cache_control(no_cache=True, must_revalidate=True, no_store=True)
    def dispatch(self, request, *args, **kwargs):
        return super(RosterGenerateView, self).dispatch(request, *args, **kwargs)

    def get_content_disposition(self, context):
        return "attachment; filename=Roster_{buildings}.csv" % {'buildings': context["buildings"]}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})

        return kwargs

    def form_valid(self, form):
        self.template_name = self.report_template_name

        buildings = form.cleaned_data['buildings']
        resident_list = []

        for building in buildings:
            try:
                resident_list.extend(reverse_address_lookup(community=building.community.name, building=building.name))
            except ObjectDoesNotExist:
                pass

        return self.render_to_response(self.get_context_data(form=form,
                                                             buildings=buildings,
                                                             resident_list=resident_list))

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
        context = super(RosterGenerateView, self).get_context_data(**kwargs)

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
