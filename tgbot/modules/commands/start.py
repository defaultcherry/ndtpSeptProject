from modules import dp, db
from modules.models import main_keyboard

from aiogram import types
from aiogram.filters import CommandStart


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    with db.Session() as session:
        user = db.get_user(telegram_id=message.from_user.id)
        if user is None:
            session.add(db.TgBotUser(telegram_id=message.from_user.id))
            session.commit()
    await message.react([types.ReactionTypeEmoji(emoji="👌")])
    await message.reply(
        "*Добро пожаловать в бота!*\n\n"
        "Здесь Вы можете проверить свои навыки в программировании, соревнуясь за самый быстрый, оптимизированный и "
        "чистый код.\n\n*Как определяется лучшее решение?*\nРешение определяется лучшим, если оно работает быстро, "
        "не расходует много оперативной памяти и соблюдает стандарты написания кода (для Python, например, PEP8).\n\n"
        "*Как взаимодействовать с ботом?*\nСнизу должна появиться клавиатура с кнопками, нажимая на которые, Вы "
        "можете взаимодействовать с ботом.",
        parse_mode="Markdown",
        reply_markup=main_keyboard(user_id=message.from_user.id),
    )
