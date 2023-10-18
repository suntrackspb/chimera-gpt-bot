import base64
import io
import os
import random
import string
import time
from io import BytesIO

from PIL import Image


def save_image(data, chat_id):
    image_data = base64.b64decode(data)
    img = Image.open(BytesIO(image_data))
    timestamp = time.time()
    uid = ''.join(random.sample(string.ascii_letters + string.digits, 12))
    name = f"{chat_id}_{uid}_{timestamp}.webp"
    path = os.getenv("IMG_PATH")
    if not os.path.exists(path):
        os.makedirs(path)
    file = os.path.join(path, name)
    img.save(file, format='WebP')
    return {"filename": name, "image": io.BytesIO(base64.b64decode(data))}
