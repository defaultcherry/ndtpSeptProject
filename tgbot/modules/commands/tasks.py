from modules import dp, db, models, form_router
from modules.test_solution import test_solution
from modules.models import (
    main_keyboard,
    paginate_pages,
    tasks_keyboard,
    task_page_keyboard,
    SendSolutionForm
)

from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select


@dp.message(F.text == "Задачи")
async def tasks_handler(message: types.Message):
    """User will get list of tasks. When it selects the task, it can see "Tests" and "Send solution" buttons.
    Furthermore, task title, description and notes would send to user"""
    with db.Session() as session:
        sel = select(models.Task).filter_by(visible=True)
        tasks = list(session.scalars(sel).all())
        if len(tasks) == 0:
            return await message.reply(
                "Пусто...",
                reply_markup=main_keyboard(message.from_user.id)
            )
        pages = paginate_pages(tasks)
        base_text = "*Список задач*:\n\n"
        for task in pages[0]:
            base_text += f"*{task.id}\\.* {task.title} \\- 👤{len(task.solved_by)}\n"
        base_text += (
            "\nПожалуйста, выберите задачу, нажав на её номер на клавиатуре снизу\\."
        )
        await message.reply(
            base_text, reply_markup=tasks_keyboard(pages), parse_mode="MarkdownV2"
        )


@dp.callback_query(F.data == "open_tasks_list")
async def tasks_callback_handler(query: types.CallbackQuery):
    with db.Session() as session:
        sel = select(models.Task).filter_by(visible=True)
        tasks = list(session.scalars(sel).all())
        pages = paginate_pages(tasks)
        base_text = "*Список задач*:\n\n"
        for task in pages[0]:
            base_text += f"*{task.id}\\.* {task.title} \\- 👤{len(task.solved_by)}\n"
        base_text += (
            "\nПожалуйста, выберите задачу, нажав на её номер на клавиатуре снизу\\."
        )
        await query.message.edit_text(
            text=base_text, reply_markup=tasks_keyboard(pages), parse_mode="MarkdownV2"
        )


@dp.callback_query(F.data == "return_to_main")
async def return_to_main_handler(query: types.CallbackQuery):
    await query.answer()
    await query.message.delete()
    await query.message.answer(
        "Возвращаемся на главную", reply_markup=main_keyboard(query.from_user.id)
    )


@dp.callback_query(F.data.startswith("tasks_list_"))
async def tasks_list_callback_handler(query: types.CallbackQuery):
    await query.answer()
    data = query.data.removeprefix("tasks_list_")
    if data.isdigit():
        with db.Session() as session:
            sel = select(models.Task).filter_by(id=int(data))
            task = session.scalars(sel).first()
            if task is None or not task.visible:
                return
            await query.message.edit_text(
                f"*{task.title}*\n\n"
                f"{task.description}\n\n"
                + (f"_Примечание:_ {task.notes}" if task.notes else ""),
                reply_markup=task_page_keyboard(task, task.author.telegram_id == query.from_user.id),
                parse_mode="MarkdownV2",
            )


@form_router.callback_query(F.data.startswith("cancel_send_task_solution_"))
async def cancel_send_task_solution(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    data = query.data.removeprefix("cancel_send_task_solution_")
    if not data.isdigit():
        return
    with db.Session() as session:
        sel = select(models.Task).filter_by(id=int(data))
        task = session.scalars(sel).first()
        if task is None or not task.visible:
            return
        await state.clear()
        await query.message.edit_text(
            f"*{task.title}*\n\n"
            f"{task.description}\n\n"
            + (f"_Примечание:_ {task.notes}" if task.notes else ""),
            reply_markup=task_page_keyboard(task, task.author.telegram_id == query.from_user.id),
            parse_mode="MarkdownV2",
        )

@form_router.callback_query(F.data.startswith("task_send_solution_"))
async def send_task_solution_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    data = query.data.removeprefix("task_send_solution_")
    if not data.isdigit():
        return
    with db.Session() as session:
        sel = select(models.Task).filter_by(id=int(data))
        task = session.scalars(sel).first()
        if task is None or not task.visible:
            return
        await state.update_data(task_id=task.id)
        await state.set_state(SendSolutionForm.task_solution)
        await query.message.edit_text(
            "Пришлите боту Ваше решение (бот также принимает файлы в кодировке UTF-8)",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отмена",
                            callback_data=f"cancel_send_task_solution_{task.id}",
                        )
                    ]
                ]
            ),
        )

@dp.callback_query(F.data.startswith("task_delete_"))
async def delete_task_handler(query: types.CallbackQuery):
    try:
        task_id = int(query.data.removeprefix("task_delete_"))
    except ValueError:
        return
    with db.Session() as session:
        task = session.scalars(
            select(models.Task).filter_by(id=task_id)
        ).first()
        if task is None or task.author.telegram_id != query.from_user.id:
            return
        await query.message.edit_text(
            f"Вы действительно хотите удалить задачу *{task.title}*?\n\n"
            "*ВНИМАНИЕ\\!\\!\\!* Всё, что зависит от этой задачи \\(решения, соревнования и т\\.д\\.\\) будет удалено\\.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Да", callback_data=f"task_confirmed_delete_{task_id}"),
                        InlineKeyboardButton(text="Нет", callback_data=f"tasks_list_{task_id}")
                    ]
                ]
            ),
            parse_mode="MarkdownV2"
        )

@dp.callback_query(F.data.startswith("task_confirmed_delete_"))
async def confirmed_task_delete_handler(query: types.CallbackQuery):
    try:
        task_id = int(query.data.removeprefix("task_confirmed_delete_"))
    except ValueError:
        return
    with db.Session() as session:
        task = session.scalars(
            select(models.Task).filter_by(id=task_id)
        ).first()
        if task is None or task.author.telegram_id != query.from_user.id:
            return
        for solution in task.solved_by:
            session.delete(solution)
        for contest_task in task.used_in_contests:
            session.delete(contest_task)
        session.delete(task)
        session.commit()
        await query.message.edit_text(
            "Задача была удалена.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Назад к задачам", callback_data="open_tasks_list")
                    ]
                ]
            )
        )

@form_router.message(SendSolutionForm.task_solution, F.text | F.document)
async def get_user_solution_handler(message: types.Message, state: FSMContext):
    solution = message.text
    if not solution:
        solution = (
            (await message.bot.download(message.document.file_id))
            .read()
            .decode("utf-8")
        )
    data = await state.update_data(task_solution=solution)
    await message.reply(
        "Решение принято. Ожидайте вердикта",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Вернуться к задаче",
                        callback_data=f"tasks_list_{data['task_id']}"
                    )
                ]
            ]
        )
    )
    await state.clear()
    result = await test_solution(
        task_id=data['task_id'],
        user_id=message.from_user.id,
        solution=data['task_solution']
    )
    if not result:
        return
    with db.Session() as session:
        solved_task = session.scalars(
            select(models.SolvedTask).filter_by(
                id=result
            )
        ).first()
        await message.answer(
            f"*Вердикт к задаче №{solved_task.task_id}:* {solved_task.verdict.name}\n\n"
            f"*Потрачено времени на тест \\(макс\\.\\):* {str(round(solved_task.solve_time or 0, 3)).replace(".", "\\.")} сек\\.\n"
            # f"*Потрачено памяти на тест \\(макс\\.\\):* {str(round(solved_task.megabyte_usage or 0, 3)).replace(".", "\\.")} МБ\n"
            f"*Ошибка на тесте:* {solved_task.failed_test or 'отсутствует'}\n"
            f"*Ошибок форматирования кода:* {solved_task.code_format_errors or 'нет'}",
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Вернуться к задаче",
                            callback_data=f"tasks_list_{data['task_id']}"
                        )
                    ]
                ]
            )
        )
