from aiogram.filters import Command

from modules import dp, db
from modules.models import admin_panel_main_keyboard

from aiogram import types, F


@dp.message(Command("sendmessage"))
async def send_message_handler(message: types.Message):
    if db.get_owner().telegram_id != message.from_user.id:
        return
    args = message.md_text.split()
    if len(args) < 3:
        return await message.reply(
            "Больше аргументов укажи"
        )
    _, user_id, *text = args
    await message.bot.send_message(
        user_id,
        " ".join(text),
        parse_mode="MarkdownV2"
    )
    await message.reply("Выполнено")


@dp.message(F.text == "Админ-панель")
async def admin_panel_handler(message: types.Message):
    user = db.get_user(telegram_id=message.from_user.id)
    if not any(
        [
            user.can_create_tasks,
            user.can_create_contests,
            user.is_owner,
            user.can_manage_permissions,
        ]
    ):
        return

    await message.reply(
        "Используйте кнопки ниже для выполнения необходимых действий",
        reply_markup=admin_panel_main_keyboard(
            user.can_create_tasks,
            user.can_create_contests,
            user.can_manage_permissions,
            user.is_owner,
        ),
    )
