import os
from common.settings import *

SECRET_KEY = '@pzaeeu_u+ggea4cvbhkl3b%1dhtmor3%zv4h7d5%ks38506=k'

DEBUG = True

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT')
    }
}


STATIC_URL = '/inventory_management_system/static/'
STATIC_ROOT = '/inventory_management_system/static/'

STATICFILES_DIRS = (
    #This lets Django's collectstatic store our bundles
    os.path.join(BASE_DIR, './static'),
)

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = ''

# Odoo settings
AUTH_ODOO_HOSTNAME = os.environ.get('ODOO_USERNAME')
AUTH_ODOO_PROTOCOL = os.environ.get('ODOO_PROTOCOL')
AUTH_ODOO_BINDPORT = os.environ.get('ODOO_PORT')
AUTH_ODOO_DATABASE = os.environ.get('ODOO_DATABASE')
AUTH_ODOO_GROUPFILTER = os.environ.get('ODOO_FILTER')
