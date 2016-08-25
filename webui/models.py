'''
Created on Jul 22, 2016

@author: jivan
'''
import datetime

from django.contrib.auth.models import User
from django.db import models


class SubscriptionHistory(models.Model):
    user = models.ForeignKey(User)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=6, decimal_places=2)
    stripe_confirm = models.CharField(max_length=80, null=True, blank=True, default=None)
    begin_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    @classmethod
    def expires(cls, user):
        user_subscriptions = SubscriptionHistory.objects.values('end_date').filter(user=user)\
            .exclude(stripe_confirm=None).order_by('-end_date')
        if len(user_subscriptions) == 0:
            expires = datetime.date(datetime.MINYEAR, 1, 1)
        else:
            expires = user_subscriptions[0]['end_date']

        return expires

    @classmethod
    def is_active(cls, user):
        user_history = SubscriptionHistory.objects.values('end_date')\
            .filter(user=user).exclude(stripe_confirm=None).order_by('-end_date')
        if len(user_history) == 0:
            active = False
        elif datetime.datetime.now() <= user_history[0]['end_date']:
            active = True
        else:
            active = False

        return active
