from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_loads_correctly(client):
    resp = client.get(reverse('tonetutor_homepage'))
    assert resp.status_code == 200
