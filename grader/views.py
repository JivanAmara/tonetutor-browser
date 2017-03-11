import os

from django.conf import settings
from django.views.generic import TemplateView
from tonerecorder.models import RecordedSyllable
from logging import getLogger
logger = getLogger(__name__)

class GraderView(TemplateView):
    template_name = 'grader/grader.html'

    def get(self, request, *args, **kwargs):
        rss = RecordedSyllable.objects.order_by('user__username', 'syllable__sound', 'syllable__tone')
        i = 0
        while (rss[i].audio_mp3 is None):
            i += 1
        rs = rss[i]

        self.expected_sound = rs.syllable.sound
        self.expected_tone = rs.syllable.tone
        logger.debug(rs.audio_mp3)
        syllable_filename = os.path.basename(rs.audio_mp3)
        self.recording_url = os.path.join(
            settings.MEDIA_URL, settings.SYLLABLE_AUDIO_DIR, syllable_filename
        )

        return TemplateView.get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c.update({
            'recording_url': self.recording_url,
            'expected_sound': self.expected_sound,
            'expected_tone': self.expected_tone,
        })
        return c
