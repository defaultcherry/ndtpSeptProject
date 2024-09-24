import logging

from aiogram.filters import Command

from modules import form_router
from modules.models import main_keyboard

from aiogram import F
from aiogram import types
from aiogram.fsm.context import FSMContext


@form_router.message(F.text == "Отмена")
@form_router.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.reply(
        "Отменено. Возвращаюсь на главную.",
        reply_markup=main_keyboard(message.from_user.id),
    )
