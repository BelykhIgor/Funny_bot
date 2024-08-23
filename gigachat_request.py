import re
import shutil
import asyncio
import requests
from gigachat_get_token import get_token
import requests
import json
from config import RQ_UID, AUTH, URL_REQUEST
import logging

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

url = f"{URL_REQUEST}"
response_media = {}

async def post_request_gigachat(user_request):
    logger.info("Start get TOKEN")
    token = await get_token(RQ_UID, AUTH)
    logger.info("Start post GigaChat")
    payload = json.dumps({
      "model": "GigaChat",
      "messages": [
        {
          "role": "user",
          "content": f"{user_request}"
        }
      ],
      "temperature": 1,
      "top_p": 0.1,
      "n": 1,
      "stream": False,
      "max_tokens": 512,
      "repetition_penalty": 1
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify='chain.pem')

    response_content = response.json()
    # print(response.text)

    print(response_content)
    answer = response_content["choices"][0]["message"]["content"]
    return answer

async def post_request_gigachat_media(user_request):
    response_media = {}
    logger.info("Start get TOKEN")
    token = await get_token(RQ_UID, AUTH)
    logger.info("Start post GigaChat")
    payload = json.dumps({
        "model": "GigaChat",
        "messages": [
            {
                "role": "system",
                "content": "Ты — Василий Кандинский"
            },
            {
                "role": "user",
                "content": f"{user_request}"
            }
        ],
        "function_call": "auto",
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # Отправляем запрос на генерацию картинки
    response_query = requests.request("POST", url, headers=headers, data=payload, verify='chain.pem')
    response_content = response_query.json()
    response_query = response_content['choices'][0]['message']['content']
    logger.info(f"Get from media post query - {response_query}")

    # Вырезаем идентификатор из строки
    try:
        img_match = re.search(r'<img src="([^"]+)" fuse="true"/>', response_query)
        img_id = img_match.group(1)
        logger.info(f"IMAGE ID - {img_id}")
        # Загрузка и сохранение изображения
        url_media = f"https://gigachat.devices.sberbank.ru/api/v1/files/{img_id}/content"
        logger.info(f"URL_MEDIA - {url_media}")
        headers = {
            'Accept': 'application/jpg',
            'Authorization': f'Bearer {token}'
        }

        response = requests.request("GET", url_media, headers=headers, stream=True, verify='chain.pem')
        with open(f'images/{img_id}.jpg', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        response_media["id_media"] = f'{img_id}.jpg'
        return response_media
    except Exception as e:
        logger.info(f"Error, request - {e}")
        response_media["answer_text"] = response_query
        return response_media

