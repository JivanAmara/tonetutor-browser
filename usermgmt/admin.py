from django.contrib import admin
from usermgmt.models import RegistrationCode, UserProfile

admin.site.register(RegistrationCode, admin.ModelAdmin)
admin.site.register(UserProfile, admin.ModelAdmin)