import asyncio
import os
import time
from pathlib import Path
from typing import Any

from PIL import Image
from celery import Celery
from rembg import remove

from bot.loader import bot
from bot.utils.constants import rm_bg

celery = Celery("tasks", broker="redis://localhost:6379")


def remove_files(uid: str):
    try:
        os.remove(f"bot/temp/{uid}")
        os.remove(f"bot/temp/{uid}_no_bg.png")
        os.remove(f"bot/temp/{uid}_no_bg.webp")
    except FileNotFoundError as ex:
        pass


async def send_result(uid: str, filename: Any):
    with open(filename, "rb") as file:
        await bot.send_document(uid, file)
        remove_files(uid)


@celery.task
def remove_background_from_image(filename: str, img_type: str):
    filename = Path(filename)
    name = filename.name.split(".")
    log = f"bot/img_log/{name[0]}-{time.time()}.webp"
    with filename.open("rb") as f:
        img = Image.open(f)
        rm = remove(img)
        if img_type == "webp":
            new_file = Path.joinpath(filename.parent, f"{name[0]}_no_bg.webp")
            rm.save(new_file, format="webp")
        else:
            new_file = Path.joinpath(filename.parent, f"{name[0]}_no_bg.png")
            rm.save(new_file, format="png")
        rm.save(log, format="WebP")
    asyncio.run(send_result(name[0], new_file))

