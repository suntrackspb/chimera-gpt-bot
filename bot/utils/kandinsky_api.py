import asyncio
import base64
import json
import os
import io
import random
import string
import time
from PIL import Image
from io import BytesIO
import requests

url = 'https://api.fusionbrain.ai/web/api/v1/text2image/run?model_id=1'


async def generate_image(style, desc, tlg):
    img_id = await run_generate(style, desc)
    if img_id is not False:
        data = await get_image(img_id)
        file = await save_image(data, tlg)
        return {"filename": file, "image": io.BytesIO(base64.b64decode(data))}


def generate_string():
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(16))


random_number = generate_string()
boundary = f"boundary=----WebKitFormBoundary{random_number}"
content_type = f"multipart/form-data; {boundary}"

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': content_type,
    'DNT': '1',
    'Origin': 'https://editor.fusionbrain.ai',
    'Referer': 'https://editor.fusionbrain.ai/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"'
}


async def run_generate(style, query):
    payload = {
        "type": "GENERATE",
        "style": style,
        "width": '1024',
        "height": '1024',
        "generateParams":
            {
                "query": query
            }
    }
    body = list()
    body.append(b'--' + f'----WebKitFormBoundary{random_number}'.encode('ascii'))
    body.append('Content-Disposition: form-data; name="params"'.encode('ascii'))
    body.append('Content-Type: application/json'.encode('ascii'))
    body.append(b'')
    body.append(json.dumps(payload).encode('utf-8'))
    body.append(b'--' + f'----WebKitFormBoundary{random_number}'.encode('ascii') + b'--')

    response = requests.post(url, headers=headers, data=b"\r\n".join(body))
    # print(b"\r\n".join(body))

    try:
        response.raise_for_status()
        # print(response.json())
        uuid = response.json()['uuid']
        # print(uuid)
        return uuid
    except requests.exceptions.HTTPError as err:
        print('HTTP error occurred:', err)
        return False
    except requests.exceptions.JSONDecodeError as err:
        print('Error decoding JSON response:', err)
        return False
    except Exception as err:
        print('An error occurred:', err)
        return False


async def get_image(uid):
    while True:
        # print("iter")
        await asyncio.sleep(7)
        response = requests.get(f'https://api.fusionbrain.ai/web/api/v1/text2image/status/{uid}', headers=headers)
        data = response.json()
        # print(data)
        if data['status'] == 'DONE':
            img = data['images'][0]
            # print(img)
            return img


async def save_image(data, tid):
    image_data = base64.b64decode(data)
    img = Image.open(BytesIO(image_data))
    timestamp = time.time()
    name = f"{tid}_{timestamp}.webp"
    path = os.getenv("IMG_PATH")
    # path = '/home/den/Projects/Python/gpt-bot/img'
    if not os.path.exists(path):
        os.makedirs(path)
    file = os.path.join(path, name)
    img.save(file, format='WebP')
    return name
