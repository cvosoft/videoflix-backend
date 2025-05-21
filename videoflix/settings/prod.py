# videoflix/settings/prod.py

from .base import *

DEBUG = False
ALLOWED_HOSTS = ['api.predigtflix.de']

MEDIA_ROOT = '/mnt/blockstorage/media'
MEDIA_URL = '/media/'
FILE_UPLOAD_TEMP_DIR = '/mnt/blockstorage/tmp_uploads'
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB
