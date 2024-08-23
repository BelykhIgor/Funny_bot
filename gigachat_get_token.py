import asyncio
import requests
from config import URL_GET_TOKEN
import logging

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


url = f"{URL_GET_TOKEN}"


async def get_token(rq_uid:str, auth:str) -> str:
    logger.info("Get token GigaChat")
    payload='scope=GIGACHAT_API_PERS'
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
      'RqUID': f'{rq_uid}',
      'Authorization': f'Basic {auth}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    data = response.json()

    auth_token = data["access_token"]
    return auth_token


