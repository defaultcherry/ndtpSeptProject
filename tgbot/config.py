import os
import secrets

from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
access_code = secrets.choice(list(str(i) for i in range(10000, 99999)))
api_token = os.getenv("API_TOKEN")
