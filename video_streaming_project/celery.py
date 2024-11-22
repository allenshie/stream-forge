from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_streaming_project.settings')

app = Celery('video_streaming_project')
app.config_from_object('video_streaming_project.celeryconfig')
app.autodiscover_tasks()