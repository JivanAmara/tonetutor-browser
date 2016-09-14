'''
Created on Sep 14, 2016

@author: jivan
'''
import json
import os
from pprint import pprint

from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_tone_check(client):
    call_command('populate_hanzi_basics')
    # Login
    email = 'test@test.com'
    password = '/?#password123'
    User.objects.create_user(username=email, password=password)
    login_data = {'username': email, 'password': password}
    resp = client.post(reverse('auth_login'), login_data, follow=True)
    assert resp.status_code == 200

    containing_dir = os.path.abspath(os.path.dirname(__file__))
    audio_filename = 'qu1.mp3'
    audio_filepath = os.path.join(containing_dir, audio_filename)
    f = open(audio_filepath, 'rb')

    tc_data = {
        'attempt': f,
        'extension': 'mp3',
        'expected_sound': 'qu',
        'expected_tone': '1',
    }

    html_resp = client.post(reverse('tone-check'), tc_data, follow=True)
    f.close()
    assert len(html_resp.content) > 0
    print(html_resp.content)
    json_resp = json.loads(html_resp.content.decode(html_resp.charset))
    assert json_resp == {'status': True, 'tone': 1}
