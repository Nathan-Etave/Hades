import os
from app import create_app

app = create_app(is_worker=True)
app.app_context().push()

from app.extensions import celery