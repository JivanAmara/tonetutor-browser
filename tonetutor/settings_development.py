'''
Created on Jul 22, 2016

@author: jivan
'''
from tonetutor.settings import *

DEBUG = True

FB_APP_ID = '1164657436935072'

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'tonetutor-media/')

LOG_FILEPATH = os.path.join(os.path.dirname(__file__), 'tonetutor_development.log')
LOGGING['handlers']['file']['filename'] = LOG_FILEPATH

# 0 is www.mandarintt.com, 1 is test-01.mandarintt.com.
#    These are set in tonetutor fixture 'sites_data.json'
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'db.sqlite3'),
    }
}
