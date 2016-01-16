"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 1.9b1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')#2)_4q&%xsulm^ry-9s0+nxk%s%ag9gx09z_7$jhv1lmj(dwq'

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
    'django.middleware.csrf.CsrfViewMiddleware',
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
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'


# CUSTOMIZATION
# ---------------------------------------------------------------------------------------------------------------------
VERSION = '1.0.0'

SITE_ID = 1

LOGIN_URL = '/admin/login'

PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

TEMPLATES[0].update({'DIRS': [os.path.join(BASE_DIR, 'config/templates'), ]})

FIXTURE_DIRS = ['config/fixtures']

SITE_HEADER = 'Site Header Template'

# STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'var/www/static')

STATICFILES_DIRS = [
    # os.path.join(PROJECT_DIR, "var/www/static"),
    # '/var/www/static/',
    os.path.join(BASE_DIR, "config/static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'var/www/media')

LANGUAGES = (
    ('en', 'English'),
    ('af', 'Afrikaans'),
    ('zh-hans', '简体中文'),
    ('se', 'Svenska'),
)

MIDDLEWARE_CLASSES += ['django.middleware.locale.LocaleMiddleware', ]
MIDDLEWARE_CLASSES += ['django.contrib.flatpages.middleware.FlatpageFallbackMiddleware', ]

FORMAT_MODULE_PATH = 'config.formats'


DJANGO_CONTRIB = [
    'django.contrib.flatpages',
    'django.contrib.sites',
]

EXTENSIONS = [
    'import_export',
    'rest_framework',
    'reversion',
    # 'guardian',
    'mptt',
    # 'adminsortable',
    'django_select2',
    # 'feincms',
    'ckeditor',
]

PROJECT_APPS = [
    # 'fact_book',
    'administration',
    # 'config',
    'demo_app',
    'version_demo',
]

INSTALLED_APPS = INSTALLED_APPS + DJANGO_CONTRIB + EXTENSIONS + PROJECT_APPS

from .plugins.task_runner import *
from .plugins.rest_framework import *
from .plugins.ckeditor import *

# Development override
CELERY_ALWAYS_EAGER = True

# from .plugins.database import *

# import yaml
#
# with open(os.path.join(BASE_DIR, 'config/project.yml', 'r')) as f:
#     project_setup = yaml.load(f)
