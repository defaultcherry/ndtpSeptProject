from modules import dp, db
from modules.models import (
    settings_main_keyboard,
    main_keyboard,
    notification_settings_inline_keyboard,
    TgBotUser,
)

from aiogram import F
from aiogram import types
from aiogram.types import CallbackQuery
from sqlalchemy import select


@dp.message(F.text == "Настройки")
@dp.message(F.text == "Назад к настройкам")
async def settings_main_handler(message: types.Message):
    await message.reply(
        "Что конкретно Вы хотите настроить в боте?",
        reply_markup=settings_main_keyboard(),
    )


@dp.message(F.text == "Назад на главную")
async def back_to_main_keyboard_handler(message: types.Message):
    await message.reply(
        "Возвращаемся", reply_markup=main_keyboard(message.from_user.id)
    )


@dp.message(F.text == "Удалить аккаунт")
async def delete_account_settings_handler(message: types.Message):
    await message.reply(
        "Нельзя (пока что)\n\nЧто конкретно Вы хотите настроить в боте?",
        reply_markup=settings_main_keyboard(),
    )


@dp.message(F.text == "Уведомления")
async def notifications_settings_handler(message: types.Message):
    with db.Session() as session:
        user = session.scalars(
            select(TgBotUser).filter_by(telegram_id=message.from_user.id)
        ).first()
        await message.reply(
            "Нажмите на кнопку для изменения настройки уведомлений",
            reply_markup=notification_settings_inline_keyboard(
                new_contest_enabled=user.new_contest_notifications_enabled,
                new_task_enabled=user.new_task_notifications_enabled,
                contest_results_enabled=user.contest_results_notifications_enabled,
            ),
        )


@dp.callback_query(F.data.startswith("notifications_switch_"))
async def notifications_query_handler(query: CallbackQuery):
    if query.data == "notifications_switch_return_to_settings":
        await query.answer()
        await query.message.delete()
        await query.message.answer(
            "Что конкретно Вы хотите настроить в боте?",
            reply_markup=settings_main_keyboard(),
        )
        return
    with db.Session() as session:
        user = session.scalars(
            select(TgBotUser).filter_by(telegram_id=query.from_user.id)
        ).first()
        match query.data.removeprefix("notifications_switch_"):
            case "new_contest":
                user.new_contest_notifications_enabled = (
                    not user.new_contest_notifications_enabled
                )
            case "new_task":
                user.new_task_notifications_enabled = (
                    not user.new_task_notifications_enabled
                )
            case "contest_results":
                user.contest_results_notifications_enabled = (
                    not user.contest_results_notifications_enabled
                )
            case "all_on":
                user.new_contest_notifications_enabled = True
                user.new_task_notifications_enabled = True
                user.contest_results_notifications_enabled = True
            case "all_off":
                user.new_contest_notifications_enabled = False
                user.new_task_notifications_enabled = False
                user.contest_results_notifications_enabled = False

        session.commit()
        await query.answer()
        await query.message.edit_reply_markup(
            reply_markup=notification_settings_inline_keyboard(
                new_contest_enabled=user.new_contest_notifications_enabled,
                new_task_enabled=user.new_task_notifications_enabled,
                contest_results_enabled=user.contest_results_notifications_enabled,
            )
        )


@dp.message(F.text == "О боте")
async def about_bot_handler(message: types.Message):
    await message.reply(
        "Данный бот был разработан в рамках сентябрьской образовательной смены 2024 года Национального детского "
        "технопарка Болвахом Алексеем. Основная цель бота: создание системы для нахождения наилучшего решения по "
        "скорости, расходу ресурсов железа и стилю кода.\n\n"
        "*Поддерживаемые языки программирования:* Python 3.12.\n\n"
        "*Используемые проверки:*\n"
        "- Запуск кода: `python -OO executable.py`\n"
        "- Проверка стиля кода: `ruff check executable.py --config \"lint.select = ['E', 'F', 'UP', 'B', 'SIM', "
        "'I']\" --ignore-noqa --isolated --statistics`\n\n"
        "Что конкретно Вы хотите настроить в боте?",
        parse_mode="Markdown",
        reply_markup=settings_main_keyboard(),
    )
