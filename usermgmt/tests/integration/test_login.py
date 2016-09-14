'''
Created on Sep 13, 2016

@author: jivan
'''
from django.contrib.auth.models import User
from django.urls import reverse
import pytest


def test_expected_field_names(client):
    expected_field_names = ['username', 'password']
    resp = client.get(reverse('auth_login'), follow=True)
    assert resp.status_code == 200

    form = resp.context['form']
    for field in form.fields:
        assert field in expected_field_names

@pytest.mark.django_db
def test_login_successful(client):
    email = 'test@test.com'
    password = '/?#password123'
    User.objects.create_user(username=email, password=password)

    post_data = {'username': email, 'password': password}

    resp = client.post(reverse('auth_login'), data=post_data, follow=True)

    assert resp.status_code == 200
    user = User.objects.get(username=email)
    assert user.is_authenticated()
