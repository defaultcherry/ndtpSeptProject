from aiogram.utils.keyboard import InlineKeyboardBuilder

from .users import Task
from modules import db
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

__all__ = [
    "main_keyboard",
    "settings_main_keyboard",
    "notification_settings_inline_keyboard",
    "profile_keyboard",
    "tasks_keyboard",
    "admin_panel_main_keyboard",
    "task_page_keyboard",
    "created_tasks_keyboard",
]


def main_keyboard(user_id: int):
    keyboard = [
        [KeyboardButton(text="Задачи"), KeyboardButton(text="Доска лидеров")],
        [KeyboardButton(text="Мой профиль"), KeyboardButton(text="Настройки")],
    ]
    user = db.get_user(telegram_id=user_id)
    if user.is_owner or user.can_create_tasks or user.can_create_contests or user.can_manage_permissions:
        keyboard.append([KeyboardButton(text="Админ-панель")])
    keyboard.append([KeyboardButton(text="Скрыть клавиатуру")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True
    )


def settings_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Уведомления"), KeyboardButton(text="О боте")],
            [KeyboardButton(text="Назад на главную")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def notification_settings_inline_keyboard(
    new_contest_enabled: bool, new_task_enabled: bool, contest_results_enabled: bool
):
    status = {True: "✅", False: "❌"}
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{status[new_contest_enabled]} Новое соревнование",
                    callback_data="notifications_switch_new_contest",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{status[new_task_enabled]} Новая задача",
                    callback_data="notifications_switch_new_task",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{status[contest_results_enabled]} Результат соревнования",
                    callback_data="notifications_switch_contest_results",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Включить всё", callback_data="notifications_switch_all_on"
                ),
                InlineKeyboardButton(
                    text="Выключить всё", callback_data="notifications_switch_all_off"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад к настройкам",
                    callback_data="notifications_switch_return_to_settings",
                )
            ],
        ],
        resize_keyboard=True,
    )


def profile_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Мои задачи"),
                KeyboardButton(text="Мои соревнования"),
            ],
            [
                KeyboardButton(text="Решённые задачи"),
                KeyboardButton(text="Решённые соревнования"),
            ],
            [KeyboardButton(text="Назад на главную")],
        ],
        resize_keyboard=True,
    )


def tasks_keyboard(tasks: list[list[Task]]):
    control_panel = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="<<", callback_data="tasks_list_start"),
                InlineKeyboardButton(text="<", callback_data="tasks_list_prev"),
                InlineKeyboardButton(
                    text=f"1/{len(tasks)}", callback_data="tasks_list_page_1"
                ),
                InlineKeyboardButton(text=">", callback_data="tasks_list_next"),
                InlineKeyboardButton(text=">>", callback_data="tasks_list_end"),
            ],
            [
                InlineKeyboardButton(
                    text="Назад на главную", callback_data="return_to_main"
                )
            ],
        ]
    )
    builder = InlineKeyboardBuilder()
    for page in tasks:
        for task in page:
            builder.button(text=str(task.id), callback_data=f"tasks_list_{task.id}")
    builder.adjust(5)
    builder.attach(InlineKeyboardBuilder.from_markup(control_panel))
    return builder.as_markup()


def task_page_keyboard(task: Task, is_task_owner: bool = False):
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="📩 Отправить решение",
                callback_data=f"task_send_solution_{task.id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="Тесты",
                callback_data=f"task_show_tests_{task.id}"
            ),
            InlineKeyboardButton(
                text="Мои попытки",
                callback_data=f"task_show_attempts_{task.id}"
            )
        ],
        [],
        [
            InlineKeyboardButton(
                text="🔙 Назад к списку задач", callback_data=f"open_tasks_list"
            )
        ],
    ]
    if is_task_owner:
        inline_keyboard[2].append(
            InlineKeyboardButton(
                text="Все решения",
                callback_data=f"task_show_solutions_{task.id}"
            )
        )
        inline_keyboard[2].append(
            InlineKeyboardButton(
                text="Удалить задачу",
                callback_data=f"task_delete_{task.id}"
            )
        )
    else:
        inline_keyboard[2].append(
            InlineKeyboardButton(
                text="Профиль автора",
                url=f"tg://user?id={task.author.telegram_id}"
            )
        )
    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )


def created_tasks_keyboard(tasks: list[list[Task]]):
    control_panel = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="<<", callback_data="tasks_authored_start"),
                InlineKeyboardButton(text="<", callback_data="tasks_authored_prev"),
                InlineKeyboardButton(
                    text=f"1/{len(tasks)}", callback_data="tasks_authored_page_1"
                ),
                InlineKeyboardButton(text=">", callback_data="tasks_authored_next"),
                InlineKeyboardButton(text=">>", callback_data="tasks_authored_end"),
            ],
            [
                InlineKeyboardButton(
                    text="Назад на главную", callback_data="return_to_main"
                )
            ],
        ]
    )
    builder = InlineKeyboardBuilder()
    for page in tasks:
        for task in page:
            builder.button(text=str(task.id), callback_data=f"tasks_authored_{task.id}")
    builder.adjust(5)
    builder.attach(InlineKeyboardBuilder.from_markup(control_panel))
    return builder.as_markup()


def admin_panel_main_keyboard(
    create_task: bool, create_contest: bool, manage_permissions: bool, owner: bool
):
    keyboard = [[], [], [KeyboardButton(text="Назад на главную")]]
    if create_task or owner:
        keyboard[0].append(KeyboardButton(text="Создать задачу"))
    if create_contest or owner:
        keyboard[0].append(KeyboardButton(text="Создать соревнование"))
    if manage_permissions or owner:
        keyboard[1].append(KeyboardButton(text="Управление пользователями"))
    if owner:
        keyboard[1].append(KeyboardButton(text="Для владельца"))
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
