from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from usermgmt.models import UserProfile, SubscriptionHistory


class UserProfileView(TemplateView):
    template_name = 'usermgmt/user_profile.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.color_theme_display_name = request.user.profile.color_theme_display_text()

        expire_date = SubscriptionHistory.expires(request.user)
        dttoday = datetime.today()
        today = date(year=dttoday.year, month=dttoday.month, day=dttoday.day)
        if expire_date >= today:
            sem = 'Your subscription will end on {}.'.format(expire_date.strftime('%b %d, %Y'))
        else:
            sem = 'Your subscription ended on {}.'.format(expire_date.strftime('%b %d, %Y'))

        self.subscription_expiry_message = sem

        return TemplateView.get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = TemplateView.get_context_data(self, **kwargs)
        c.update({
            'color_theme_display_name': self.color_theme_display_name,
            'subscription_expiry_message': self.subscription_expiry_message,
        })
        return c

class SetColorThemeView(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        color_theme = request.GET.get('theme_name')
        if color_theme in ['greys', 'inverted', 'purple']:
            request.user.profile.color_theme = color_theme.lower()
            request.user.profile.save()

        resp = HttpResponseRedirect(reverse('tonetutor_user-profile'))
        return resp

def color_theme_context_processor(request):
    try:
        ct = request.user.profile.color_theme
    except:
        ct = UserProfile.default_color_theme

    context_update = {
        'color_theme': ct,
    }
    return context_update
