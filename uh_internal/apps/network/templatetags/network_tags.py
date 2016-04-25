"""
.. module:: uh_internal.apps.network.templatetags.network_tags
   :synopsis: University Housing Internal Network Template Tags

.. moduleauthor:: Thomas Willson <thomas.willson@icloud.com>

"""

from django.template import Library, Template
from django.template.context import Context

register = Library()


@register.simple_tag
def login_attempt_tr(login_attempt):
    tr_template = """
    {% load staticfiles %}
    <tr>
        <td>{{ attempt.time|date:"m/d/y H:i:s" }}</td>
        <td>{{ attempt.username }}</td>
        <td>{{ attempt.get_result_display }}</td>
        <td>
            <a aria-hidden="true" title='Login Attempt' popover-data-url='{% url "network:login_attempt_info_frame" pk=attempt.id %}'>
                <img src="{% static 'images/icons/info.png' %}" style="width: 16px; height: 16px">
            </a>
        </td>
    </tr>
    """

    return Template(tr_template).render(Context({'attempt': login_attempt}))
