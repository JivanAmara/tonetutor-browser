'''
Created on Jul 22, 2016

@author: jivan
'''
from tonetutor.settings import *

DEBUG = True
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'tonetutor-media/')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'db.sqlite3'),
    }
}
