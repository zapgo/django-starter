"""
Django settings for default project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from .plugins.api_keys import *
from .plugins.rest_framework import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$jb4u!^j9so#g4*n_+ructl@z!c#_z@$cqw*$5-^ld#k=4v1(6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Africa/Johannesburg'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'


# CUSTOMIZATION
# ---------------------------------------------------------------------------------------------------------------------
VERSION = '1.0.0'

SITE_ID = 1

LOGIN_URL = '/admin/login'

PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

TEMPLATES[0].update({'DIRS': [os.path.join(BASE_DIR, 'config/templates'), ]})

FIXTURE_DIRS = ['config/fixtures']

SITE_HEADER = 'Zapgo Engine'

CACHE_DIR = os.path.join(PROJECT_DIR, 'var/cache')

# STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'var/www/static')

STATICFILES_DIRS = [
    # os.path.join(PROJECT_DIR, "var/www/static"),
    # '/var/www/static/',
    os.path.join(BASE_DIR, "config/static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'var/www/media')

AUTH_USER_MODEL = 'administration.UserBasic'

LANGUAGES = (
    ('en', 'English'),
    ('af', 'Afrikaans'),
)

MIDDLEWARE_CLASSES += ['django.middleware.locale.LocaleMiddleware', ]
MIDDLEWARE_CLASSES += ['django.contrib.flatpages.middleware.FlatpageFallbackMiddleware', ]

FORMAT_MODULE_PATH = 'config.formats'

DJANGO_CONTRIB = [
    'django.contrib.flatpages',
    'django.contrib.sites',
]

EXTENSIONS = [
    #'rest_framework_swagger',
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'rest_auth.registration',
]

PROJECT_APPS = [
    'administration',
    'zapgo_engine',
]

INSTALLED_APPS = INSTALLED_APPS + DJANGO_CONTRIB + EXTENSIONS + PROJECT_APPS


CURRENCY_MAPPING = {
    'currency': {
        'USD': {
            'SFOX': 'USD'
        },
        'ZAR': {
            'BITX': 'ZAR',
        },
        'EUR': {
            'KRAKEN': 'ZEUR',
        },
        'XBT': {
            'BITX': 'XBT',
            'KRAKEN': 'XXBT',
        }
    },
    'pairs': {
        'XBT_EUR': {
            'KRAKEN': 'XXBTZEUR'
        },
        'XBT_ZAR': {
            'BITX': 'XBTZAR'
        },
        'XBT_USD': {
            'SFOX': 'XBT_USD'
        }
    }
}


# TASK RUNNER
# ---------------------------------------------------------------------------------------------------------------------
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "UTC"

CELERY_CREATE_MISSING_QUEUES = True

if not DEBUG:
    CELERY_DEFAULT_QUEUE = 'zapgo-engine'
else:
    CELERY_DEFAULT_QUEUE = 'zapgo-engine-local'

CELERY_ROUTES = {'zapgo_engine.tasks.refresh_bitcoin_rates': {'queue': 'zapgo-update-rates'},
                 'zapgo_engine.tasks.refresh_forex_rates': {'queue': 'zapgo-update-rates'},
                 'zapgo_engine.tasks.run_arb_play': {'queue': 'zapgo-arbitrage'}}


BROKER_TRANSPORT = 'sqs'
BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-1',
    'visibility_timeout': 30,
    'polling_interval': 1,
}

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'refresh-bitcoin-exchange-rates': {
        'task': 'zapgo_engine.tasks.refresh_bitcoin_rates',
        'schedule': timedelta(seconds=30),
        'args': ()
    },
    'refresh-forex-rates': {
        'task': 'zapgo_engine.tasks.refresh_forex_rates',
        'schedule': timedelta(seconds=3600),  # slightly longer ensure bitcoin rate is updated first
        'args': ()
    },
}


if False:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': os.environ.get('DB_ENV_POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_ENV_POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', ''),
            'PORT': os.environ.get('DB_PORT_5432_TCP_PORT', ''),
        }
    }

