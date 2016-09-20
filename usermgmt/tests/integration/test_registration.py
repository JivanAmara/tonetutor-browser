'''
Created on Sep 13, 2016

@author: jivan
'''
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.urls.base import reverse
import pytest
from usermgmt.models import RegistrationCode


def test_expected_registration_form_fields(client):
    # While username isn't used, it's present due to subclassing of registration form.
    expected_field_names = ['username', 'email', 'password1', 'password2', 'regcode', 'ad_campaign_code']
    resp = client.get(reverse('registration_register'))
    assert resp.status_code == 200

    fields = resp.context['form'].fields
    for field in fields:
        assert field in expected_field_names

@pytest.mark.django_db
def test_register_activate(client):
    email_address = 'test@jivanamara.net'
    RegistrationCode.objects.create(code='testtest', notes='test registration code')
    post_data = {
        'email': email_address,
        'password1': '/#-password123',
        'password2': '/#-password123',
        'regcode': 'testtest',
    }
    resp = client.post(reverse('registration_register'), data=post_data, follow=True)
    if 'form' in resp.context:
        assert resp.context['form'].errors
    assert resp.status_code == 200

    assert len(mail.outbox) == 1
    user = User.objects.get(username=email_address)
    assert user.is_active == False

    body_no_newlines = mail.outbox[0].body.replace('\n', '')
    activation_url = re.sub(r'^.*http://testserver(.*)/\w.*$', r'\1', body_no_newlines)

    resp = client.get(activation_url, follow=True)
    assert resp.status_code == 200
    user = User.objects.get(username=email_address)
    assert user.is_active == True
