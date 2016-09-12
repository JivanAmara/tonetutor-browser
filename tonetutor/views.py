'''
Created on Sep 8, 2016

@author: jivan
'''
from registration.backends.hmac.views import RegistrationView
from tonetutor.forms import EmailUsernameForm
from django.conf import settings


class EmailUsernameRegistrationView(RegistrationView):
    form_class = EmailUsernameForm

    def get_context_data(self, **kwargs):
        c = RegistrationView.get_context_data(self, **kwargs)
        c.update({
            'free_trial_code': settings.TRIAL_REGISTRATION_CODE
        })
        return c
