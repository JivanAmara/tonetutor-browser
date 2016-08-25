# coding=utf-8
import calendar
import datetime
import json
from logging import getLogger
import os
from pprint import pprint
import random
import time
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.base import View
from hanzi_basics.models import PinyinSyllable
import scipy.io.wavfile
import stripe
from syllable_samples.interface import get_random_sample
from tonerecorder.models import RecordedSyllable, create_audio_path
from ttlib.characteristics.interface import generate_all_characteristics
from ttlib.normalization.interface import normalize_pipeline
from ttlib.recognizer import ToneRecognizer

from webui.forms import RecordingForm
from webui.models import SubscriptionHistory


logger = getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'webui/homepage.html'
    context_updates = {}

    def get(self, request, *args, **kwargs):
        # Get browser details
        browser_family = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version
        browser_version_string = request.user_agent.browser.version_string

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
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        attempt = request.FILES['attempt']
        extension = request.POST['extension']
        expected_sound = request.POST['expected_sound']
        expected_tone = request.POST['expected_tone']
        is_native = request.POST.get('is_native', False)

        user = request.user if type(request.user) == User else None

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
        sound, tone, display, path = get_random_sample()

        # 'css/style.css' file should exist in static path. otherwise, error will occur
        url = static(path)
        data = {
            'sound': sound,
            'tone': tone,
            'display': display,
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
        print(user.username)
        sound, tone, display, path = get_random_sample()
        self.record_tone = tone
        self.record_syllable = display
        self.audio_sample = path

        self.form = RecordingForm(initial={'expected_tone': tone})
        return TemplateView.get(self, request, *args, **kwargs)

class SubscriptionView(TemplateView):
    template_name = 'webui/subscription.html'
    month_price = 5.0

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        expires = SubscriptionHistory.expires(request.user)
        today = datetime.date.today()
        if expires < today:
            begin_date = today
        else:
            begin_date = expires

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
        self.payment_amount = sh.payment_amount
        self.begin_date = sh.begin_date
        self.end_date = sh.end_date
        self.subscription_id = sh.id
        return TemplateView.get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c.update({
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
        stripe.api_key = os.environ.get('STRIPE_API_KEY', None)

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
