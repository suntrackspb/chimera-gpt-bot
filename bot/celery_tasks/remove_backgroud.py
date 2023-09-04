from pathlib import Path

from celery import Celery

celery = Celery("tasks", broker="redis://localhost:6379")


def remove_background_from_image(tlg_id: int, filename: Path):
    pass
