from django.urls import reverse

def test_loads_correctly(client):
    resp = client.get(reverse('tonetutor_homepage'))
    assert resp.status_code == 200
