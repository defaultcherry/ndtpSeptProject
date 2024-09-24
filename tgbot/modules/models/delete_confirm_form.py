from aiogram.fsm.state import State, StatesGroup

__all__ = ["DeleteForm"]


class DeleteForm(StatesGroup):
    confirm = State()
