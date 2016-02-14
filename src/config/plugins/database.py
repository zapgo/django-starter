# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
import os

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'postgres',
#         'USER': os.environ.get('DB_ENV_POSTGRES_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_ENV_POSTGRES_PASSWORD', 'postgres'),
#         'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', ''),
#         'PORT': os.environ.get('DB_PORT_5432_TCP_PORT', ''),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOSTNAME', 'postgres'),
        'PORT': os.environ.get('POSTGRES_PORT_PORT', '5432')
    }
}
