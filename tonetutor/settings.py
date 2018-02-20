"""
Django settings for tonetutor project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os
import random
import string

TONETUTOR_VERSION = '1.4.4'

# 0 is www.mandarintt.com, 1 is test-01.mandarintt.com.
#    These are set in tonetutor fixture 'sites_data.json'
SITE_ID = 0

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', random.sample(string.printable, 80))

# Registration code used by new users for a one-day free trial
TRIAL_REGISTRATION_CODE = '4E3XB8UT'

# Facebook Application ID
FB_APP_ID = '1164657436935071'

# Log file path
LOG_FILEPATH = '/var/log/tonetutor.log'

# --- Mail settings for sending registration emails.
EMAIL_HOST = os.environ.get('EMAIL_HOST')
# Port 25 / Port 465 (SSL required) / Port 587 (TLS required)
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Build paths inside the project like this: os.path.join(PROJECT_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_ROOT = '/mnt/data-volume/tonetutor-media/'
MEDIA_URL = '/media/'
SYLLABLE_AUDIO_DIR = 'audio-files'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

ALLOWED_HOSTS = ['www.mandarintt.com', 'test.mandarintt.com', 'localhost']


ACCOUNT_ACTIVATION_DAYS = 7

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'tonetutor',
    'usermgmt',
    'tonerecorder',
    'hanzi_basics',

    # This is just to allow cascading deletes of webapi models during database curation
    'webapi',

    'webui',
    'syllable_samples',
    'django_user_agents',

    'sitetree',
    'rest_framework.authtoken',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'tonetutor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tonetutor.views.current_site_context_processor',
                'tonetutor.views.fb_app_id_context_processor',
                'usermgmt.views.color_theme_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'tonetutor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DBPASS = os.environ.get('DB_PASS')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'webvdc',  # Or path to database file if using sqlite3.
        'USER': 'webvdc',  # Not used with sqlite3.
        'PASSWORD': DBPASS,  # Not used with sqlite3.
        'HOST': 'database-host',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/tonetutor-static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': { 'format': '%(levelname)s %(filename)s:%(lineno)d %(funcName)s() - %(message)s' },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILEPATH,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
