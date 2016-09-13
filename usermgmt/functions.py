'''
Created on Sep 13, 2016

@author: jivan
'''
from usermgmt.models import SubscriptionHistory

def allowed_tutor(user):
    if user.profile.registration_code is None or user.profile.registration_code.unlimited_use:
        allowed = True
    elif SubscriptionHistory.is_active(user):
        allowed = True
    else:
        allowed = False
    return allowed
