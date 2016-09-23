'''
Created on Sep 8, 2016

@author: jivan
'''
from registration.backends.hmac.views import RegistrationView
from tonetutor.forms import EmailUsernameForm
from django.conf import settings
from django.contrib.sites.models import Site
import logging
logger = logging.getLogger(__name__)

class EmailUsernameRegistrationView(RegistrationView):
    form_class = EmailUsernameForm

    def get_context_data(self, **kwargs):
        c = RegistrationView.get_context_data(self, **kwargs)
        c.update({
            'free_trial_code': settings.TRIAL_REGISTRATION_CODE
        })
        form = c['form']
        acc = form.fields['ad_campaign_code']
        acc.initial = self.request.session.get('ad_campaign_code')

        return c

def current_site_context_processor(request):
    cs = Site.objects.get_current(request)
    return {'site': cs.domain}

def fb_app_id_context_processor(request):
    if not hasattr(settings, 'FB_APP_ID'):
        logger.error('FB_APP_ID must be set in settings file.  Shares to facebook will not work.')
        appid = ''
    else:
        appid = settings.FB_APP_ID

    return {'FB_APP_ID': appid}
