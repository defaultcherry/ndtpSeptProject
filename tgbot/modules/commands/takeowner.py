import config
import logging

from modules import dp
from modules import db

from aiogram import types
from aiogram.filters import Command


@dp.message(Command("takeowner"))
async def takeowner_handler(message: types.Message):
    if db.get_owner() is not None:
        return

    splitted = message.text.split()
    if len(splitted) <= 1:
        return await message.reply(
            "Введите команду ровно так, как было указано в консоли!"
        )

    code = splitted[1]
    if code != config.access_code:
        return

    await message.reply("Успешно! Теперь бот будет считать Вас своим владельцем.")
    logging.info(f"Добавлен владелец с ID: {message.from_user.id}")
    db.add_owner(message.from_user.id)
