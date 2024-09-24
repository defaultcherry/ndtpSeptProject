from aiogram.fsm.state import State, StatesGroup

__all__ = ["SendSolutionForm"]


class SendSolutionForm(StatesGroup):
    task_id = State()
    task_solution = State()
