import logging
import config

from aiogram import Bot, Dispatcher, Router
from .db import get_owner

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token)
dp = Dispatcher()
form_router = Router()
dp.include_router(form_router)

if get_owner() is None:
    print("\n========================================================================")
    print(
        "В боте не добавлен владелец! Пожалуйста, введите команду ниже с аккаунта, на который нужно выдать владельца, "
        "в личные сообщения Telegram-бота:\n"
    )
    print(f"/takeowner {config.access_code}")
    print("========================================================================\n")

# modules
from .commands import start
from .commands import takeowner
from .commands import keyboard_close_handler
from .commands import cancel_handler
from .commands import settings
from .commands import profile
from .commands import admin_panel
from .commands import task_create
from .commands import tasks
