# coding=utf-8
import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import scipy.io.wavfile
from ttlib.characteristics.interface import generate_all_characteristics
from ttlib.normalization.interface import normalize_pipeline
from ttlib.recognizer import ToneRecognizer

from webui.forms import RecordingForm
from webui.models import SyllableAttempt


def get_syllable_for_speaker(user):
    ''' *brief*: returns the next sound/tone pair for the user to attempt.
    '''
    available = [
        ('qi', 2, 'qí'), ('mo', 2, 'mó'), ('qu', 4, 'qù'), ('fen', 1, 'fēn'), ('hua', 4, 'huà'), ('zai', 1, 'zāi'), ('xing', 4, 'xìng'), ('nei', 4, 'nèi'), ('ba', 4, 'bà'), ('chu', 3, 'chǔ'), ('yuan', 1, 'yuān'), ('wo', 3, 'wǒ'), ('tuo', 1, 'tuō'), ('li', 2, 'lí'), ('zhong', 4, 'zhòng'), ('xiang', 2, 'xiáng'), ('you', 2, 'yóu'), ('qi', 1, 'qī'), ('zhong', 3, 'zhǒng'), ('yi', 2, 'yí'), ('dan', 4, 'dàn'), ('liao', 4, 'liào'), ('zhan', 4, 'zhàn'), ('jia', 3, 'jiǎ'), ('men', 5, 'men'), ('na', 5, 'na'), ('ran', 2, 'rán'), ('chu', 4, 'chù'), ('chang', 3, 'chǎng'), ('zhi', 2, 'zhí'), ('ru', 2, 'rú'), ('shuo', 1, 'shuō'), ('huo', 1, 'huō'), ('dang', 1, 'dāng'), ('xing', 2, 'xíng'), ('huo', 2, 'huó'), ('xin', 1, 'xīn'), ('nan', 2, 'nán'), ('ma', 2, 'má'), ('jin', 1, 'jīn'), ('dei', 3, 'děi'), ('yu', 1, 'yū'), ('you', 4, 'yòu'), ('xia', 2, 'xiá'), ('guo', 1, 'guō'), ('hao', 3, 'hǎo'), ('huo', 4, 'huò'), ('hou', 4, 'hòu'), ('ni', 1, 'nī'), ('zhang', 3, 'zhǎng'), ('guo', 2, 'guó'), ('sheng', 4, 'shèng'), ('hang', 2, 'háng'), ('nian', 3, 'niǎn'), ('mo', 4, 'mò'), ('bi', 1, 'bī'), ('de', 2, 'dé'), ('ma', 3, 'mǎ'), ('le', 5, 'le'), ('jie', 5, 'jie'), ('ge', 4, 'gè'), ('jie', 1, 'jiē'), ('suo', 1, 'suō'), ('yi', 3, 'yǐ'), ('xiang', 1, 'xiāng'), ('da', 2, 'dá'), ('xi', 3, 'xǐ'), ('jiao', 1, 'jiāo'), ('yuan', 2, 'yuán'), ('tian', 1, 'tiān'), ('jing', 1, 'jīng'), ('ren', 4, 'rèn'), ('jiu', 4, 'jiù'), ('cong', 1, 'cōng'), ('hai', 2, 'hái'), ('da', 1, 'dā'), ('shui', 4, 'shuì'), ('zheng', 1, 'zhēng'), ('jiao', 3, 'jiǎo'), ('hui', 3, 'huǐ'), ('yi', 1, 'yī'), ('chu', 1, 'chū'), ('jie', 4, 'jiè'), ('ren', 2, 'rén'), ('mo', 3, 'mǒ'), ('wei', 2, 'wéi'), ('ben', 3, 'běn'), ('zuo', 4, 'zuò'), ('zhao', 1, 'zhāo'), ('ke', 4, 'kè'), ('ying', 1, 'yīng'), ('shang', 1, 'shāng'), ('di', 2, 'dí'), ('dan', 3, 'dǎn'), ('zhu', 2, 'zhú'), ('zhu', 1, 'zhū'), ('jiu', 1, 'jiū'), ('nei', 3, 'něi'), ('zhi', 1, 'zhī'), ('ke', 3, 'kě'), ('wo', 1, 'wō'), ('nuo', 4, 'nuò'), ('shang', 5, 'shang'), ('dui', 1, 'duī'), ('zi', 4, 'zì'), ('zai', 4, 'zài'), ('shou', 3, 'shǒu'), ('duo', 1, 'duō'), ('tou', 2, 'tóu'), ('bu', 2, 'bú'), ('ri', 4, 'rì'), ('fa', 3, 'fǎ'), ('ba', 3, 'bǎ'), ('dong', 4, 'dòng'), ('na', 4, 'nà'), ('guo', 3, 'guǒ'), ('jing', 4, 'jìng'), ('kai', 1, 'kāi'), ('chang', 2, 'cháng'), ('yu', 4, 'yù'), ('shen', 1, 'shēn'), ('yue', 4, 'yuè'), ('li', 5, 'li'), ('ji', 2, 'jí'), ('xian', 2, 'xián'), ('ma', 1, 'mā'), ('wei', 1, 'wēi'), ('bing', 4, 'bìng'), ('chu', 2, 'chú'), ('bei', 4, 'bèi'), ('da', 3, 'dǎ'), ('ju', 4, 'jù'), ('shi', 3, 'shǐ'), ('ge', 2, 'gé'), ('xin', 4, 'xìn'), ('yuan', 4, 'yuàn'), ('fa', 2, 'fá'), ('na', 3, 'nǎ'), ('bu', 1, 'bū'), ('guan', 4, 'guàn'), ('kan', 4, 'kàn'), ('zhu', 4, 'zhù'), ('le', 4, 'lè'), ('yin', 1, 'yīn'), ('jiao', 4, 'jiào'), ('qi', 3, 'qǐ'), ('na', 2, 'ná'), ('ma', 4, 'mà'), ('zuo', 2, 'zuó'), ('xia', 4, 'xià'), ('guan', 3, 'guǎn'), ('lai', 4, 'lài'), ('zheng', 4, 'zhèng'), ('nian', 2, 'nián'), ('shang', 3, 'shǎng'), ('quan', 2, 'quán'), ('jin', 4, 'jìn'), ('tong', 4, 'tòng'), ('hou', 3, 'hǒu'), ('shi', 4, 'shì'), ('zhuo', 1, 'zhuō'), ('hui', 2, 'huí'), ('hua', 1, 'huā'), ('nian', 1, 'niān'), ('zhei', 4, 'zhèi'), ('si', 1, 'sī'), ('jia', 2, 'jiá'), ('guan', 1, 'guān'), ('bi', 4, 'bì'), ('bi', 3, 'bǐ'), ('si', 4, 'sì'), ('ye', 4, 'yè'), ('zi', 5, 'zi'), ('shen', 2, 'shén'), ('wo', 4, 'wò'), ('zi', 1, 'zī'), ('ji', 4, 'jì'), ('qian', 2, 'qián'), ('you', 1, 'yōu'), ('xing', 1, 'xīng'), ('fa', 4, 'fà'), ('wu', 2, 'wú'), ('kuai', 3, 'kuǎi'), ('ni', 3, 'nǐ'), ('ming', 2, 'míng'), ('cheng', 2, 'chéng'), ('hang', 1, 'hāng'), ('dai', 4, 'dài'), ('xiao', 3, 'xiǎo'), ('bu', 4, 'bù'), ('zai', 3, 'zǎi'), ('hu', 2, 'hú'), ('lai', 2, 'lái'), ('cheng', 4, 'chèng'), ('yong', 4, 'yòng'), ('mo', 1, 'mō'), ('bi', 2, 'bí'), ('hou', 2, 'hóu'), ('he', 1, 'hē'), ('jia', 1, 'jiā'), ('zi', 3, 'zǐ'), ('xian', 1, 'xiān'), ('yu', 3, 'yǔ'), ('cheng', 3, 'chěng'), ('men', 4, 'mèn'), ('xue', 2, 'xué'), ('xian', 4, 'xiàn'), ('zuo', 3, 'zuǒ'), ('huan', 2, 'huán'), ('gong', 1, 'gōng'), ('dao', 3, 'dǎo'), ('yang', 4, 'yàng'), ('zhu', 3, 'zhǔ'), ('zhe', 2, 'zhé'), ('er', 5, 'er'), ('shi', 1, 'shī'), ('jian', 3, 'jiǎn'), ('li', 4, 'lì'), ('jiang', 4, 'jiàng'), ('zheng', 3, 'zhěng'), ('xi', 4, 'xì'), ('dui', 4, 'duì'), ('shuo', 4, 'shuò'), ('er', 4, 'èr'), ('chang', 1, 'chāng'), ('yao', 3, 'yǎo'), ('xiang', 4, 'xiàng'), ('mei', 3, 'měi'), ('hao', 4, 'hào'), ('shui', 2, 'shuí'), ('yan', 2, 'yán'), ('ge', 1, 'gē'), ('yao', 2, 'yáo'), ('liao', 2, 'liáo'), ('neng', 2, 'néng'), ('jie', 3, 'jiě'), ('wei', 4, 'wèi'), ('zong', 4, 'zòng'), ('nian', 4, 'niàn'), ('fen', 4, 'fèn'), ('di', 4, 'dì'), ('dan', 1, 'dān'), ('jun', 1, 'jūn'), ('tong', 2, 'tóng'), ('ye', 1, 'yē'), ('bian', 4, 'biàn'), ('yao', 4, 'yào'), ('wu', 3, 'wǔ'), ('dai', 1, 'dāi'), ('ke', 1, 'kē'), ('yao', 1, 'yāo'), ('zhi', 4, 'zhì'), ('ma', 5, 'ma'), ('jing', 3, 'jǐng'), ('ke', 2, 'ké'), ('zhuo', 2, 'zhuó'), ('wu', 4, 'wù'), ('cong', 2, 'cóng'), ('hang', 4, 'hàng'), ('ye', 3, 'yě'), ('huan', 4, 'huàn'), ('zhao', 4, 'zhào'), ('dao', 1, 'dāo'), ('yuan', 3, 'yuǎn'), ('kuai', 4, 'kuài'), ('ta', 3, 'tǎ'), ('da', 4, 'dà'), ('er', 2, 'ér'), ('she', 4, 'shè'), ('wu', 1, 'wū'), ('hui', 4, 'huì'), ('shui', 3, 'shuǐ'), ('da', 5, 'da'), ('shang', 4, 'shàng'), ('mian', 4, 'miàn'), ('guo', 4, 'guò'), ('he', 4, 'hè'), ('men', 1, 'mēn'), ('sheng', 3, 'shěng'), ('sheng', 1, 'shēng'), ('dang', 4, 'dàng'), ('li', 3, 'lǐ'), ('chang', 4, 'chàng'), ('li', 1, 'lī'), ('you', 3, 'yǒu'), ('bu', 3, 'bǔ'), ('ta', 4, 'tà'), ('shu', 4, 'shù'), ('di', 3, 'dǐ'), ('ge', 3, 'gě'), ('ni', 4, 'nì'), ('ren', 3, 'rěn'), ('me', 5, 'me'), ('jie', 2, 'jié'), ('men', 2, 'mén'), ('ji', 1, 'jī'), ('jian', 4, 'jiàn'), ('xian', 3, 'xiǎn'), ('ni', 2, 'ní'), ('yu', 2, 'yú'), ('dou', 1, 'dōu'), ('shi', 2, 'shí'), ('fa', 1, 'fā'), ('ji', 3, 'jǐ'), ('liao', 1, 'liāo'), ('xie', 1, 'xiē'), ('zhe', 1, 'zhē'), ('zuo', 1, 'zuō'), ('kuai', 1, 'kuāi'), ('fu', 4, 'fù'), ('jiao', 2, 'jiáo'), ('xing', 3, 'xǐng'), ('suo', 3, 'suǒ'), ('kan', 1, 'kān'), ('zhao', 2, 'zháo'), ('mei', 2, 'méi'), ('zhe', 4, 'zhè'), ('cheng', 1, 'chēng'), ('wei', 3, 'wěi'), ('jin', 3, 'jǐn'), ('hua', 2, 'huá'), ('qi', 4, 'qì'), ('zhi', 3, 'zhǐ'), ('jia', 4, 'jià'), ('xia', 1, 'xiā'), ('ti', 2, 'tí'), ('fu', 2, 'fú'), ('hao', 1, 'hāo'), ('xi', 2, 'xí'), ('jiu', 3, 'jiǔ'), ('er', 3, 'ěr'), ('sheng', 2, 'shéng'), ('he', 2, 'hé'), ('di', 1, 'dī'), ('gong', 3, 'gǒng'), ('fang', 1, 'fāng'), ('zhe', 5, 'zhe'), ('ding', 4, 'dìng'), ('hui', 1, 'huī'), ('jiang', 1, 'jiāng'), ('gong', 4, 'gòng'), ('yi', 4, 'yì'), ('xi', 1, 'xī'), ('zhe', 3, 'zhě'), ('de', 5, 'de'), ('dai', 3, 'dǎi'), ('liao', 3, 'liǎo'), ('ye', 2, 'yé'), ('ta', 1, 'tā'), ('huo', 3, 'huǒ'), ('xiang', 3, 'xiǎng'), ('shi', 5, 'shi'), ('nuo', 2, 'nuó'), ('dao', 4, 'dào'), ('si', 3, 'sǐ'), ('jue', 2, 'jué'), ('jian', 1, 'jiān'), ('zhao', 3, 'zhǎo'), ('du', 1, 'dū'), ('zhong', 1, 'zhōng'),
    ]
    syllable = random.choice(available)
    return syllable

class TutorPageView(TemplateView):
    template_name = 'tutor.html'
    expected_tone = None
    result_tone = None
    record_tone = None

    def get(self, request, *args, **kwargs):
        user = request.user if hasattr(request, 'user') else None
        sound, tone, display = get_syllable_for_speaker(user)
        self.record_tone = tone
        self.form = RecordingForm(initial={'expected_tone': tone})
        return TemplateView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = RecordingForm(request.POST, request.FILES)
        if self.form.is_valid():
            recording = self.form.cleaned_data['recording']
            extension = recording.name.split('.')[-1]
            user = request.user if type(request) == User else None
            print(type(user))
            SyllableAttempt.objects.create(recording=recording, user=user)

            with NamedTemporaryFile(suffix='.{}'.format(extension)) as original:
                with NamedTemporaryFile(suffix='.wav') as normalized:
                    for chunk in recording.chunks():
                        original.write(chunk)
                    original.flush()
                    normalize_pipeline(original.name, normalized.name)
                    sample_rate, wave_data = scipy.io.wavfile.read(normalized.name)
                    sample_characteristics = generate_all_characteristics(wave_data, sample_rate)

                    tr = ToneRecognizer()
                    tone = tr.get_tone(sample_characteristics)
            self.result_tone = tone
            self.expected_tone = self.form.cleaned_data['expected_tone']

        return self.get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cd = TemplateView.get_context_data(self, **kwargs)
        cd.update({
            'recording_form': self.form,
            'result_tone': self.result_tone,
            'expected_tone': self.expected_tone,
            'record_tone': self.record_tone,
        })
        return cd
