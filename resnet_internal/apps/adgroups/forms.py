"""
.. module:: reslife_internal.adgroups.forms
   :synopsis: ResLife Internal AD Group Management Forms.

.. moduleauthor:: Alex Kavanaugh <kavanaugh.development@outlook.com>

"""

from django.forms import Form, CharField

from .validators import validate_ad_membership


class AddADUserForm(Form):
    userPrincipalName = CharField(label='Cal Poly Email Address', max_length=26, error_messages={'required': 'An email address is required'}, validators=[validate_ad_membership])
