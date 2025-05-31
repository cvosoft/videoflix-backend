# videoflix/settings/prod.py

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['api.predigtflix.de']

MEDIA_ROOT = '/mnt/blockstorage/media'
MEDIA_URL = '/media/'
FILE_UPLOAD_TEMP_DIR = '/mnt/blockstorage/tmp_uploads'
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB


CORS_ALLOWED_ORIGINS = [
    "https://predigtflix.de",
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FROM = config('AUTHEMAIL_DEFAULT_EMAIL_FROM')
EMAIL_BCC = config('AUTHEMAIL_DEFAULT_EMAIL_BCC', default=None)
EMAIL_HOST = config('AUTHEMAIL_EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('AUTHEMAIL_EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('AUTHEMAIL_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('AUTHEMAIL_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
DEFAULT_FROM_EMAIL = 'noreply@predigtflix.de'
