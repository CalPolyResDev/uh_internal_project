"""
.. module:: reslife_internal.adgroups.forms
   :synopsis: ResLife Internal AD Group Management Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import Form, CharField

from .validators import validate_ad_membership


class AddADUserForm(Form):
    alias = CharField(label='Cal Poly Alias', max_length=14, error_messages={'required': 'An alias is required'}, validators=[validate_ad_membership])
