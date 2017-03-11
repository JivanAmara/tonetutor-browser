"""tonetutor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from tonetutor.forms import EmailUsernameAuthenticationForm
from tonetutor.views import EmailUsernameRegistrationView
from usermgmt.views import UserProfileView, SetColorThemeView
from webui.views import TutorView, ToneCheck, GetSyllableView, HomePageView, SubscriptionView, \
    PaymentSuccessView, VersionView, CampaignBrowserDetails, HelpView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomePageView.as_view(), name='tonetutor_homepage'),
    url(r'^help/?$', HelpView.as_view(), name='tonetutor_help'),
    url(r'^version/?$', VersionView.as_view(), name='tonetutor_version'),
    url(r'^tutor/?$', TutorView.as_view(), name='tonetutor_tutor'),
    url(r'report_campaign_browser/?$', CampaignBrowserDetails.as_view(), name='tonetutor_api-report-homepage-browser'),
    url(r'^api/tonecheck/?$', ToneCheck.as_view(), name='tone-check'),
    url(r'^api/getsyllable/?$', GetSyllableView.as_view(), name='get-syllable'),
    url(r'^accounts/register/?$', EmailUsernameRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/profile/?$', UserProfileView.as_view(), name='tonetutor_user-profile'),
    url(r'^api/set-color-theme', SetColorThemeView.as_view(), name='tonetutor_set-color-theme'),
    url(r'^accounts/login/?$', auth_views.login, {'authentication_form': EmailUsernameAuthenticationForm}),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^subscription/?$', SubscriptionView.as_view(), name='tonetutor_subscription'),
    url(r'^payment-success/?$', PaymentSuccessView.as_view(), name='tonetutor_payment-success'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    from django.views.static import serve
    urlpatterns += [url(
        r'^media/(?P<path>.*)$'.format(settings.MEDIA_URL), serve,
        {'document_root': settings.MEDIA_ROOT}
    )]
