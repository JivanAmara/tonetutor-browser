'''
Created on Sep 13, 2016

@author: jivan
'''
import pytest
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls.base import reverse

@pytest.mark.django_db
def test_tutor_page_authenticated(client):
    email = 'test@test.com'
    password = '/?#password123'
    user = User.objects.create_user(username=email, email=email, password=password)

    login_data = {'username': email, 'password': password}
    resp = client.post(reverse('auth_login'), login_data, follow=True)
    assert resp.status_code == 200
    user = auth.get_user(client)
    assert user.is_authenticated() == True

    resp = client.get(reverse('tonetutor_tutor'), follow=True)
    # If there were a problem with the authentication the user would be redirected to the login page
    assert len(resp.redirect_chain) == 0
    assert resp.status_code == 200
