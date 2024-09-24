from aiogram.fsm.state import State, StatesGroup

__all__ = ["CreateTaskForm"]


class CreateTaskForm(StatesGroup):
    title = State()
    description = State()
    notes = State()
    visible = State()
    tests_in = State()
    tests_out = State()
    tests_visible = State()
