from __future__ import annotations

import os
from celery import Celery
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Daikokuten.settings')
app = Celery('Daikokuten')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'generate-predictions-every-5-minutes': {
        'task': 'modelling.tasks.generate_predictions',
        'schedule': 300.0,
        'args': (),
    },
}
