"""
Django settings for diseaseMatcher project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#KEY IS deployed to heroku environment variable; stored locally in text file diseaseMatcher/secret_key_holder.txt
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'diseaseMatcherApp',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'diseaseMatcher.urls'

WSGI_APPLICATION = 'diseaseMatcher.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'diseasematcherdb',
        'USER': 'root',
        'PASSWORD': 't0blaive',
        'HOST': '127.0.0.1'
    }
}
'''

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#this is needed for sstatic template tag.  TODO: TRYING: REMOVE lead/trail SLASHES FOR COMPATIBILITY WITH dj-static and Heroku?
STATIC_ROOT = 'diseaseMatcherApp'

#I think this is redundant with BASE_DIR, but for now I'm following directions exactly from:
#https://devcenter.heroku.com/articles/django-assets
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)