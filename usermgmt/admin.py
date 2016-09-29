from django.contrib import admin
from usermgmt.models import RegistrationCode, UserProfile, AdCampaign, SubscriptionHistory

admin.site.register(RegistrationCode, admin.ModelAdmin)
admin.site.register(UserProfile, admin.ModelAdmin)
admin.site.register(AdCampaign, admin.ModelAdmin)
admin.site.register(SubscriptionHistory, admin.ModelAdmin)
