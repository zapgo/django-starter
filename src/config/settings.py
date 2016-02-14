from .default import *

DEBUG = False
if os.environ.get('DEBUG') == "True":
    DEBUG = True

ALLOWED_HOSTS = ['*']

VERSION = '0.0.1'
SITE_ID = os.environ.get("SITE_ID", 1)
SITE_HEADER = 'Site Header Template'
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
LOGIN_URL = '/admin/login'

TEMPLATES[0].update({'DIRS': [os.path.join(BASE_DIR, 'config/templates'), ]})
FIXTURE_DIRS = ['config/fixtures']
STATICFILES_DIRS = [
    # os.path.join(PROJECT_DIR, "var/www/static"),
    # '/var/www/static/',
    os.path.join(BASE_DIR, "config/static"),
]

# STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'var/www/static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'var/www/media')

MIDDLEWARE_CLASSES += [
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'axes.middleware.FailedLoginMiddleware',
]

DJANGO_CONTRIB = [
    'django.contrib.flatpages',
    'django.contrib.sites',
]

EXTENSIONS = [
    'import_export',
    'rest_framework',
    'reversion',
    'guardian',
    'mptt',
    'django_select2',
    'ckeditor',
    'axes',
]

PROJECT_APPS = [
    # 'fact_book.apps.AdminConfig',
    'administration',
    # 'config',
    'demo_app',
]

INSTALLED_APPS = INSTALLED_APPS + DJANGO_CONTRIB + EXTENSIONS + PROJECT_APPS

if True:
    from .plugins.task_runner import *
    from .plugins.rest_framework import *
    from .plugins.ckeditor import *
    from .plugins.database import *

# Site specific overrides
if SITE_ID == 1:
    DEBUG = True
    CELERY_ALWAYS_EAGER = True

ANONYMOUS_USER_ID = -1
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'guardian.backends.ObjectPermissionBackend')
