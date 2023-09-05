import os

import requests
from celery import Celery
from bot.celery_tasks.clear_temp import remove_files

url = os.getenv("REMBG_API")
key = os.getenv("REMBG_KEY")

celery = Celery("tasks", broker=os.getenv("REDIS"))


@celery.task
def api_remove_background(uid: str, flag: str, filename: str):
    img_type = "png"
    if bool(flag):
        img_type = "webp"

    headers = {
        "Content-Type": "multipart/form-data"
    }

    params = {
        "key": key,
        "uid": uid,
        "img_type": img_type
    }

    files = {
        "file": open(filename, "rb")
    }

    response = requests.post(url, headers=headers, params=params, files=files)

    if response.status_code == 200:
        print("Successful Response")
        print(response.json())
    elif response.status_code == 422:
        print("Validation Error")
        print(response.json())
    else:
        print("Error:", response.status_code)

    remove_files(uid)
