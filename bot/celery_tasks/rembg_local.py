import asyncio
import os
from pathlib import Path
from PIL import Image
from celery import Celery
from rembg import remove

from bot.loader import bot
from bot.celery_tasks.clear_temp import remove_files

celery = Celery("tasks", broker=os.getenv("REDIS"))


async def send_result(uid: str, filename: Path) -> None:
    try:
        with open(filename, "rb") as file:
            await bot.send_document(uid, file)
            remove_files(uid)
    except Exception as ex:
        print(ex)
    finally:
        remove_files(uid)


@celery.task
def local_remove_background(uid: str, flag: str, filename: str) -> None:
    img_type = "png"
    if bool(flag):
        img_type = "webp"
    filename = Path(filename)
    with filename.open("rb") as f:
        img = Image.open(f)
        rm = remove(img)
        new_filename = f"{uid}_no_bg.{img_type}"
        new_file = filename.parent / new_filename
        rm.save(new_file, format=img_type)
    asyncio.run(send_result(uid, new_file))

