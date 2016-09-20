'''
Created on Sep 19, 2016

@author: jivan
'''
from django.db import models
from usermgmt.models import AdCampaign

class HomePageCampaignDetails(models.Model):
    campaign = models.ForeignKey(AdCampaign, null=True, blank=True)
    browser_family = models.CharField(max_length=100)
    browser_version_string = models.CharField(max_length=100)
    media_recorder_supported = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
