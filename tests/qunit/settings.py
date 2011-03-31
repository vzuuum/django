import os

BASE_PATH = os.path.dirname(__file__)

QUNIT_TEST_DIRECTORY = os.path.join(BASE_PATH, 'tests')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'urls'
TEMPLATE_DIRS = [os.path.join(BASE_PATH, 'templates'),]
INSTALLED_APPS = (
    'django_qunit',
)
