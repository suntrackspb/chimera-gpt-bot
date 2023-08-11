import json
import os

import aiohttp

from utils.constants import db_day, db_user


async def make_request(prompt, chat_id):
    url = 'https://chimeragpt.adventblocks.cc/api/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("CHIMERA_API_KEY")}'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': prompt
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as response:
            response_text = await response.json()
            answer = {}
            if 'error' in response_text:
                answer['role'] = 'error'
                answer['content'] = f"Ошибка на стороне ChatGPT: {response_text['error']['message']}"
                return response_text['choices'][0]['message']
            db_user.upd_gpt_count(chat_id, response_text['usage'])
            db_day.execute_counter(chat_id, response_text['usage']['total_tokens'])
            return response_text['choices'][0]['message']
