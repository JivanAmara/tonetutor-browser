'''
Created on Jul 22, 2016

@author: jivan
'''
from django.db import models
from django.contrib.auth.models import User

class SyllableAttempt(models.Model):
    recording = models.FileField()
    user = models.ForeignKey(User, null=True, blank=True)

    predicted_tone = models.IntegerField(null=True, blank=True)
    expected_tone = models.IntegerField(null=True, blank=True)
