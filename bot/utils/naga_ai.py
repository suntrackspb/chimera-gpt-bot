import os
import openai
import requests

from bot.utils.constants import db_day, db_user
from bot.utils.save_images import save_image
from bot.utils.msg_templates import SDXL_ERROR


openai.api_key = os.getenv("AI_KEY")
openai.api_base = "https://api.naga.ac/v1"


def send_telegram_message(chat_id, message):
    url_send_msg = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url_send_msg, data=data)
    return response.json()


async def generate_image(chat_id: str, model: str, prompt: str, count: int = 1) -> list[dict]:
    try:
        response = openai.Image.create(
            model=model,
            prompt=prompt,
            n=count,
            size="1024x1024",
            response_format="base64",
            premium=True
        )
        images = []
        for i in response['data']:
            images.append(save_image(i['b64_json'], chat_id))
        return images
    except Exception as ex:
        print("===" * 30)
        print(ex)
        print("===" * 30)
        send_telegram_message(chat_id, SDXL_ERROR)


async def generate_chatgpt(chat_id: str, prompt: str) -> dict:
    response_text = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=prompt,
        allow_fallback=True
    )

    answer = {}

    if 'error' in response_text:
        answer['role'] = 'error'
        answer['content'] = f"Ошибка на стороне ChatGPT: {response_text['error']['message']}"
        return response_text['choices'][0]['message']
    db_user.upd_gpt_count(chat_id, response_text['usage'])
    db_day.execute_counter(chat_id, response_text['usage']['total_tokens'])
    choices = response_text.get('choices')
    if choices is not None:
        return choices[0].get('message')
