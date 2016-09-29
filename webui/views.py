# coding=utf-8
import calendar
import datetime
import json
from logging import getLogger
import os
from pprint import pprint
import random
import re
import time
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.base import View
from gunicorn.http.wsgi import Response
from hanzi_basics.models import PinyinSyllable
from rest_framework.authtoken.models import Token
import scipy.io.wavfile
import stripe
from syllable_samples.interface import get_random_sample
from tonerecorder.models import RecordedSyllable, create_audio_path
from ttlib.characteristics.interface import generate_all_characteristics
from ttlib.normalization.interface import normalize_pipeline
from ttlib.recognizer import ToneRecognizer

from usermgmt.functions import allowed_tutor
from usermgmt.models import SubscriptionHistory, AdCampaign
from webui.forms import RecordingForm
from webui.models import HomePageCampaignDetails


logger = getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'webui/homepage.html'
    context_updates = {}

    def get(self, request, *args, **kwargs):
        # Get browser details
        browser_family = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version
        browser_version_string = request.user_agent.browser.version_string
        request.session['ad_campaign_code'] = request.GET.get('c')

        self.context_updates = {
            'browser_family': browser_family,
            'browser_version': browser_version,
            'browser_version_string': browser_version_string,
        }

        return TemplateView.get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context.update(self.context_updates)
        return context

class CampaignBrowserDetails(View):
    def post(self, request, *args, **kwargs):
        campaign_code = request.session.get('ad_campaign_code')
        if campaign_code:
            try:
                campaign = AdCampaign.objects.get(code=campaign_code)
            except AdCampaign.DoesNotExist:
                campaign = None
        else:
            campaign = None

        browser_family = request.user_agent.browser.family
        browser_version_string = request.user_agent.browser.version_string
        media_recorder_supported = request.POST['media_recorder_supported'].lower() == 'true'

        HomePageCampaignDetails.objects.create(
            campaign=campaign, browser_family=browser_family,
            browser_version_string=browser_version_string,
            media_recorder_supported=media_recorder_supported
        )
        return HttpResponse('{"status": "ok"}')

class ToneCheck(View):
    ''' *brief*: provides a web-api to check the predicted tone of an audio sample.
        *note*: Saves the audio sample for later analsis in model RecordedSyllable.
        *input*: POST with file 'attempt' and values 'extension', 'expected_sound', 'expected_tone',
            'is_native'.
        *return*: JSON-encoded object with 'status' and 'tone' attributes.
            'status' is a boolean indicating if the call was successful.
            'tone' is an integer 1-5 indicating the tone or null indicating that the predictor
                can't tell which tone it is.
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token_header = request.META.get('HTTP_AUTHORIZATION')
        auth_token = re.sub(r'Token', '', token_header)
        auth_token = auth_token.strip()
        attempt = request.FILES['attempt']
        extension = request.POST['extension']
        expected_sound = request.POST['expected_sound']
        expected_tone = request.POST['expected_tone']
        is_native = request.POST.get('is_native', False)

        user = Token.objects.get(key=auth_token).user

        s = PinyinSyllable.objects.get(sound=expected_sound, tone=expected_tone)
        rs = RecordedSyllable(native=is_native, user=user, syllable=s, file_extension=extension)
        original_path = rs.create_audio_path('original')
        rs.audio_original = original_path
        rs.save()
        with open(original_path, 'wb') as f:
            f.write(attempt.read())

        with open(original_path, 'rb') as original:
            with NamedTemporaryFile(suffix='.wav') as normalized:
                normalize_pipeline(original_path, normalized.name)
                sample_rate, wave_data = scipy.io.wavfile.read(normalized.name)
                # --- Deal with sample that's too short to accurately analyze
                # minimum length (seconds)
                min_length = 0.15
                attempt_length = len(wave_data) / sample_rate
                print('Attempt length {}{}: {}'.format(
                    expected_sound, expected_tone, attempt_length)
                )
                if attempt_length < min_length:
                    tone = None
                else:
                    sample_characteristics = generate_all_characteristics(wave_data, sample_rate)

                    tr = ToneRecognizer()
                    tone = tr.get_tone(sample_characteristics)

        result = {
            'status': True,
            'tone': tone
        }
        return HttpResponse(json.dumps(result))


class GetSyllableView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        sound, tone, display, path, hanzi = get_random_sample()

        # 'css/style.css' file should exist in static path. otherwise, error will occur
        url = static(path)
        data = {
            'sound': sound,
            'tone': tone,
            'display': display,
            'hanzi': hanzi,
            'url': url
        }

        resp = HttpResponse(json.dumps(data))
        return resp


class TutorView(TemplateView):
    template_name = 'webui/tutor.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            token, created_ignored = Token.objects.get_or_create(user=user)
            self.auth_token = token.key
        except Exception as ex:
            self.auth_token = ''

        if allowed_tutor(user):
            sound, tone, display, path, hanzis = get_random_sample()
#             self.record_tone = tone
#             self.record_syllable = display
#             self.audio_sample = path

            self.form = RecordingForm(initial={'expected_tone': tone})
            ret = TemplateView.get(self, request, *args, **kwargs)
        else:
            ret = HttpResponseRedirect(reverse('tonetutor_subscription'))

        return ret

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c.update({
            'auth_token': self.auth_token,
        })
        return c

class SubscriptionView(TemplateView):
    template_name = 'webui/subscription.html'
    month_price = 5.0

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        expires = SubscriptionHistory.expires(request.user)
        today = datetime.date.today()

        # Generate a begin date for the user's next subscription period &
        #    a message regarding when the user's subscription expired / will expire.
        if expires < today:
            begin_date = today
            if request.user.profile.registration_code is None \
                or request.user.profile.registration_code.unlimited_use:
                expiration_msg = \
                    "You have a special account and don't need to pay to use ToneTutor; "\
                    "however, you're welcome to contribute if you'd like."
            else:
                expiration_msg = 'Your subscription expired on {}'.format(
                    SubscriptionHistory.expires(request.user)
                )
        else:
            begin_date = expires
            expiration_msg = 'Your subscription will expire on {}'.format(
                SubscriptionHistory.expires(request.user)
            )

        # Make an end_date one month after begin_date
        try:
            end_date = begin_date.replace(month=begin_date.month + 1)
        except ValueError:
            if begin_date.month == 12:
                # If we're at the end of the year, reset the month to January
                end_date = begin_date.replace(year=begin_date.year + 1, month=1)
            else:
                # If the next month is too short to contain our day, use the last day of the month
                max_day = calendar.monthrange(begin_date.year, begin_date.month + 1)[1]
                end_date = begin_date.replace(month=begin_date.month + 1, day=max_day)

        sh = SubscriptionHistory(
            user=request.user, begin_date=begin_date, end_date=end_date,
            payment_amount=self.month_price
        )
        sh.save()

        # Default to a single month for $5
        self.stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        self.expiration_msg = expiration_msg
        self.payment_amount = sh.payment_amount
        self.begin_date = sh.begin_date
        self.end_date = sh.end_date
        self.subscription_id = sh.id
        return TemplateView.get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c.update({
            'stripe_publishable_key': self.stripe_publishable_key,
            'expiration_msg': self.expiration_msg,
            'subscription_price': self.payment_amount,
            'begin_date': self.begin_date,
            'end_date': self.end_date,
            'subscription_id': self.subscription_id,
        })
        return c

class PaymentSuccessView(TemplateView):
    template_name = 'webui/payment_success.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        POST = request.POST
        sh = SubscriptionHistory.objects.get(id=POST['subscription_id'])
        stipe_token = POST['stripeToken']
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

        # --- Double-Check the total reported via the form in case of tampering.
        # Prices for all print types of this size
        if sh.payment_amount != float(POST['subscription_price']):
            msg = 'Price mismatch: {} != {}'.format(POST['subscription_price'], sh.payment_amount)
            logger.error(msg)
            raise Exception(msg)
        elif sh.user != request.user:
            msg = 'User mismatch: {} != {}'.format(request.user, sh.user)
            logger.error(msg)
            raise Exception(msg)


        # Get the credit card details submitted by the form
        token = POST['stripeToken']

        # Create a charge: this will charge the user's card
        try:
            description = \
                "Purchase of one month ToneTutor subscription for ${}".format(sh.payment_amount)
            charge = stripe.Charge.create(
                amount=int(sh.payment_amount * 100),  # Amount in cents
                currency="usd",
                source=token,
                description=description
            )
            pprint(charge)
            sh.stripe_confirm = charge['id']
            sh.payment_date = datetime.datetime.fromtimestamp(charge['created'])
            sh.save()
            self.success = True
            self.error_msg = None
        except stripe.error.CardError as e:
            # The card has been declined
            self.success = False
            self.error_msg = e
            pprint(e)

        self.begin_date = sh.begin_date
        self.end_date = sh.end_date

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c.update({
            'success': self.success,
            'begin_date': self.begin_date,
            'end_date': self.end_date,
            'error_msg': self.error_msg,
        })
        return c

class VersionView(View):
    def get(self, request):
        v = settings.TONETUTOR_VERSION
        resp = HttpResponse('Version: {}'.format(v))
        return resp

class HelpView(TemplateView):
    template_name = 'webui/help.html'
