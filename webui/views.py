# coding=utf-8
import json
import os
import random
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.base import View
import scipy.io.wavfile
from syllable_samples.interface import get_random_sample
from ttlib.characteristics.interface import generate_all_characteristics
from ttlib.normalization.interface import normalize_pipeline
from ttlib.recognizer import ToneRecognizer
from django.contrib.staticfiles.templatetags.staticfiles import static

from webui.forms import RecordingForm
from webui.models import SyllableAttempt


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
    def post(self, request, *args, **kwargs):
        attempt = request.FILES['attempt']
        extension = request.POST['extension']

        user = request.user if type(request.user) == User else None
        username = user.username if user else 'none'
        SyllableAttempt.objects.create(recording=attempt, user=user)

        with NamedTemporaryFile(suffix='.{}'.format(extension)) as original:
            with NamedTemporaryFile(suffix='.wav') as normalized:
                for chunk in attempt.chunks():
                    original.write(chunk)
                original.flush()
                normalize_pipeline(original.name, normalized.name)
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

    def get(self, request, *args, **kwargs):
        user = request.user if hasattr(request, 'user') else None
        sound, tone, display, path = get_random_sample()
        self.record_tone = tone
        self.record_syllable = display
        self.audio_sample = path

        self.form = RecordingForm(initial={'expected_tone': tone})
        return TemplateView.get(self, request, *args, **kwargs)
