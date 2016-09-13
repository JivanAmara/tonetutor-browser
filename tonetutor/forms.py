'''
Created on Sep 8, 2016

@author: jivan
'''
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model, forms as auth_forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from registration.forms import RegistrationFormUniqueEmail

from usermgmt.models import RegistrationCode


User = get_user_model()

class EmailUsernameForm(RegistrationFormUniqueEmail):
    regcode = forms.CharField(max_length=8, required=True, label='Registration Code')

    def __init__(self, *args, **kwargs):
        super(EmailUsernameForm, self).__init__(*args, **kwargs)
        ufield = self.fields['username']
        ufield.widget = forms.widgets.HiddenInput()
        ufield.label = ''
        ufield.required = False

    def clean_regcode(self):
        regcode = self.cleaned_data['regcode']
        if not RegistrationCode.objects.filter(code=settings.TRIAL_REGISTRATION_CODE):
            RegistrationCode.objects.create(
                code=settings.TRIAL_REGISTRATION_CODE, notes='Free one-day trial'
            )
        if not RegistrationCode.objects.filter(code=regcode).exists():
            raise ValidationError('Invalid Registration Code')
        return regcode

    def clean(self):
        if 'email' in self.cleaned_data:
            self.cleaned_data[User.USERNAME_FIELD] = self.cleaned_data['email']
        super(EmailUsernameForm, self).clean()

    def save(self, commit=True):
        user = super(EmailUsernameForm, self).save(commit)
        regcode = RegistrationCode.objects.get(code=self.cleaned_data['regcode'])
        # This attribute is checked for in post-save code in usermgmt.models
        user.registration_code = regcode
        return user

class EmailUsernameAuthenticationForm(AuthenticationForm):
    # Override AuthenticationForm to label username as 'Email'
    def __init__(self, request=None, *args, **kwargs):
        super(EmailUsernameAuthenticationForm, self).__init__(request=request, *args, **kwargs)
        self.fields['username'].label = 'Email'
