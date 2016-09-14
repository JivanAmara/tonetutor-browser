'''
Created on Sep 14, 2016

@author: jivan
'''
from django.urls import reverse

def test_profile_page_loads_correctly(client):
    resp = client.get(reverse('tonetutor_user-profile'))
    assert resp.status_code == 200
