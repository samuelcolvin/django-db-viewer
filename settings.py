import os, sys

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
HOME_DIR = os.path.expanduser('~')
ON_SERVER = False
if 'linux' in sys.platform.lower():
    import platform
    if 'virtual' in platform.platform():
        ON_SERVER = True
if ON_SERVER:
    DEBUG = False
else:
    DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (('Samuel Colvin', 'samcolvin@gmail.com'),)

MANAGERS = ADMINS

if ON_SERVER:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'u',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'sqlite.db',
        }
    }

ALLOWED_HOSTS = []

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
MEDIA_URL = '/media/'
MEDIA_RELATIVE_ROOT = 'media'
MEDIA_ROOT = os.path.join(SITE_ROOT, MEDIA_RELATIVE_ROOT)
if ON_SERVER:
    STATIC_URL = 'www.adsf.com/static/'
    STATIC_ROOT = os.path.join(HOME_DIR, 'static')
    SCRIPT_NAME = ''
    FORCE_SCRIPT_NAME = ''

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h%@u+2_75t*%6qsi2)b!(sl$wsr1imip)hky%b&gkbkeenf3!_'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request'
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'


TEMPLATE_DIRS = (os.path.join(SITE_ROOT, 'templates'),)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'bootstrapform',
    'DbViewer'
]

if DEBUG:
    INSTALLED_APPS.extend(['south'])

INSTALLED_APPS = tuple(INSTALLED_APPS)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CUSTOM_DATE_FORMAT = '%Y-%m-%d'
CUSTOM_DT_FORMAT = '%Y-%m-%d %H:%M:%S %Z'
CUSTOM_SHORT_DT_FORMAT = '%I:%M %p, %d-%m-%y'
DATETIME_FORMAT = 'Y-m-d H:i:s'
SHORT_DATETIME_FORMAT = DATETIME_FORMAT

SITE_TITLE = 'Database Viewer'

# INSTALLED_APPS = tuple(list(INSTALLED_APPS) + ['debug_toolbar'])
# MIDDLEWARE_CLASSES = tuple(list(MIDDLEWARE_CLASSES) + ['debug_toolbar.middleware.DebugToolbarMiddleware'])
#  
# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': lambda request: request.user.username == 'scolvin',
# }
#  
# DEBUG_TOOLBAR_PANELS = (
#     'debug_toolbar.panels.version.VersionDebugPanel',
#     'debug_toolbar.panels.timer.TimerDebugPanel',
#     'debug_toolbar.panels.profiling.ProfilingDebugPanel',
# )