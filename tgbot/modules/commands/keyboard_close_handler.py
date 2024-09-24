from aiogram.types import ReplyKeyboardRemove

from modules import dp

from aiogram import F
from aiogram import types


@dp.message(F.text == "Скрыть клавиатуру")
async def close_keyboard_handler(message: types.Message):
    await message.reply(
        "Клавиатура скрыта. Чтобы вернуть её обратно, напишите /start",
        reply_markup=ReplyKeyboardRemove(),
    )
