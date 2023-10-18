import asyncio
import json
import os
import time

import requests

from bot.utils.constants import db_img, styles_prompt
# from bot.utils.kandinsky_api import generate_image
from bot.utils.naga_ai import generate_image
from bot.utils.msg_templates import styles
from celery import Celery

url = os.getenv("REMBG_API")
key = os.getenv("REMBG_KEY")

celery = Celery("tasks", broker=os.getenv("REDIS"))


def get_url(func):
    return f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/{func}"


def send_telegram_file(chat_id, file, desc, style):
    url_send_photo = get_url("sendPhoto")
    files = {"photo": open(f"{os.getenv('IMG_PATH')}/{file}", "rb")}
    text = f'Style: {style}\nPrompt: ```python {desc}```'
    data = {"chat_id": chat_id, "caption": text, 'parse_mode': "MarkdownV2"}
    response = requests.post(url_send_photo, data=data, files=files)
    # os.remove(file)
    return response.json()


def send_telegram_gallery(chat_id, file):
    url_send_msg = get_url("sendMessage")
    text = "Вы можете поделиться этим изображением, опубликовав его в нашей галереи:"
    keyboard = json.dumps({'inline_keyboard': [[{"text": "Опубликовать", "callback_data": file}]]})
    data = {"chat_id": chat_id, "text": text, 'parse_mode': "MarkdownV2", 'reply_markup': keyboard}
    response = requests.post(url_send_msg, data=data)
    return response.json()


def delete_message(chat_id, message_id):
    url_del_msg = get_url("deleteMessage")
    data = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url_del_msg, data=data)


@celery.task
def run_generate_image(uid: str, message_id: str, model: str, count: int, style: str, desc: str) -> None:
    # img = asyncio.run(generate_image(style=style, desc=desc, tlg=uid))
    images = asyncio.run(generate_image(
        chat_id=uid,
        model=model,
        prompt=f"{desc} {styles_prompt[style]}",
        count=count
    ))
    if type(images) is list:
        delete_message(uid, message_id)
        delete_message(uid, int(message_id) - 1)
        delete_message(uid, int(message_id) - 2)
        for img in images:
            db_img.add_row(uid, img['filename'], desc, style)
            send_telegram_file(uid, img['filename'], desc, style)
            send_telegram_gallery(uid, img['filename'])
            time.sleep(1)
    # img = await generate_image(style=style, desc=desc, tlg=uid)

    # delete_message(uid, message_id)
    # delete_message(uid, int(message_id) - 1)
    # delete_message(uid, int(message_id) - 2)



