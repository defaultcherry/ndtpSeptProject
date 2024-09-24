from modules import dp, db
from modules.models import profile_keyboard, created_tasks_keyboard

from aiogram import types, F, md
from aiogram.enums import ParseMode


@dp.message(F.text == "Мой профиль")
async def profile_handler(message: types.Message):
    user = db.get_user(telegram_id=message.from_user.id)
    base_text = f"Профиль пользователя {md.code(message.from_user.full_name)}\n\nID в базе данных: {md.bold(user.id)}\n"
    if user.created_contests:
        base_text += f"Создано соревнований: {md.bold(len(user.created_contests))}\n"
    if user.created_tasks:
        base_text += f"Создано задач: {md.bold(len(user.created_tasks))}\n"
    if user.solved_contests:
        base_text += f"Решено соревнований: {md.bold(len(user.solved_contests))}\n"
    if user.solved_tasks:
        base_text += f"Отправлено решений задач: {md.bold(len(user.solved_tasks))}\n"
    await message.reply(
        base_text, reply_markup=profile_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
    )


@dp.message(F.text == "Мои задачи")
async def my_tasks_handler(message: types.Message):
    tasks = db.get_user(telegram_id=message.from_user.id).created_tasks
    if len(tasks) == 0:
        return await message.reply("Пусто...")
    await message.reply(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus luctus rutrum sem at bibendum. Lorem "
        "ipsum dolor sit amet, consectetur adipiscing elit. Mauris lacinia libero turpis, lobortis sollicitudin lectus "
        "dictum quis. Aliquam erat volutpat. Donec leo turpis, semper vel tempus at, volutpat a risus. Proin sed sem "
        "eget nisl posuere scelerisque eu ac mi. Cras euismod velit id odio faucibus, nec interdum eros viverra. Nulla "
        "imperdiet nec ante id varius.",
        reply_markup=created_tasks_keyboard(tasks),
    )
