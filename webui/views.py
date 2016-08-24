# coding=utf-8
import json
import os
import random
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
from syllable_samples.interface import get_random_sample
from tonerecorder.models import RecordedSyllable, create_audio_path
from ttlib.characteristics.interface import generate_all_characteristics
from ttlib.normalization.interface import normalize_pipeline
from ttlib.recognizer import ToneRecognizer

from webui.forms import RecordingForm


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
