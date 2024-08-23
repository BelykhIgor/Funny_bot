import os

from dotenv import load_dotenv

load_dotenv()

RQ_UID = os.environ.get("RQ_UID")
AUTH = os.environ.get("AUTH")
URL_REQUEST = os.environ.get("URL_REQUEST")
URL_GET_TOKEN = os.environ.get("URL_GET_TOKEN")
BOT_TOKEN = os.environ.get("BOT_TOKEN")