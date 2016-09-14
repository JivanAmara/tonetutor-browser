'''
Created on Sep 14, 2016

@author: jivan
'''
import json
from pprint import pprint

from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_get_syllable(client):
    # Expected keys in json response
    expected_keys = ['display', 'sound', 'tone', 'url']

    # Log in
    email = 'test@test.com'
    password = '/?#password123'
    User.objects.create_user(username=email, password=password)

    post_data = {'username': email, 'password': password}
    resp = client.post(reverse('auth_login'), data=post_data, follow=True)
    assert resp.status_code == 200

    http_resp = client.get(reverse('get-syllable'), follow=True)
    assert http_resp.status_code == 200
    assert len(http_resp.content) > 0
    json_resp = json.loads(http_resp.content.decode(http_resp.charset))
    for k in expected_keys:
        assert k in json_resp
    print('JSON Response:')
    pprint(json_resp)
