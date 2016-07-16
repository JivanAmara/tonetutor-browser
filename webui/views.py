from django.http import HttpResponse
from django.views.generic import TemplateView
from webui.forms import RecordingForm
from ttlib.normalization.interface import normalize_pipeline
from ttlib.characteristics.interface import generate_all_characteristics
from ttlib.recognizer import ToneRecognizer
import scipy.io.wavfile
from django.core.files.temp import NamedTemporaryFile

class TutorPageView(TemplateView):
    template_name = 'tutor.html'

    def get(self, request, *args, **kwargs):
        self.form = RecordingForm()

        return TemplateView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = RecordingForm(request.POST, request.FILES)
        if self.form.is_valid():
            resp = HttpResponse('Valid')

            recording = self.form.cleaned_data['recording']
            extension = recording.name.split('.')[-1]
            with NamedTemporaryFile(suffix='.{}'.format(extension)) as original:
                with NamedTemporaryFile(suffix='.wav') as normalized:
                    original.write(recording.read())
                    original.seek(0)
                    normalize_pipeline(original.name, normalized.name)
                    sample_rate, wave_data = scipy.io.wavfile.read(normalized.name)
                    sample_characteristics = generate_all_characteristics(wave_data, sample_rate)

                    tr = ToneRecognizer()
                    tone = tr.get_tone(sample_characteristics)
            resp = HttpResponse('That sounds like tone {}'.format(tone))
        else:
            resp = HttpResponse('Invalid')
        return resp

    def get_context_data(self, **kwargs):
        cd = TemplateView.get_context_data(self, **kwargs)
        cd.update({
            'recording_form': self.form,
        })
        return cd
