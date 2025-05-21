# videoflix/celery.py
import os
from celery import Celery

# Umgebung lesen oder fallback auf dev
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "videoflix.settings.dev")
)

app = Celery("videoflix")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()