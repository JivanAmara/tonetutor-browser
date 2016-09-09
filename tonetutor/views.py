'''
Created on Sep 8, 2016

@author: jivan
'''
from registration.backends.hmac.views import RegistrationView
from tonetutor.forms import EmailUsernameForm

class EmailUsernameRegistrationView(RegistrationView):
    form_class = EmailUsernameForm
