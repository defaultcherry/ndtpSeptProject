import os

from asyncio import sleep

from modules import db, form_router
from modules.models import CreateTaskForm, Task, admin_panel_main_keyboard, TgBotUser

from aiogram import types, F, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from sqlalchemy import select


@form_router.message(F.text == "Создать задачу")
async def create_new_task_handler(message: types.Message, state: FSMContext):
    user = db.get_user(telegram_id=message.from_user.id)
    if not any([user.can_create_tasks, user.is_owner]):
        return

    await state.set_state(CreateTaskForm.title)
    await message.reply(
        "Пожалуйста, введите название задачи.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отмена")]], resize_keyboard=True
        ),
    )


@form_router.message(CreateTaskForm.title, F.text)
async def get_task_title_handler(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateTaskForm.description)
    await message.answer(
        "Ответ принят.\n\nТеперь напишите описание Вашей задачи. Форматирование описания будет сохранено.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отмена")]], resize_keyboard=True
        ),
    )


@form_router.message(CreateTaskForm.description, F.text)
async def get_task_desc_handler(message: types.Message, state: FSMContext):
    await state.update_data(description=message.md_text)
    await state.set_state(CreateTaskForm.notes)
    await message.answer(
        "Описание принято.\n\nТеперь напишите примечания для задачи. Они будут отображаться под примерами ввода/вывода. "
        'Форматирование будет сохранено. Если их указание не требуется, нажмите кнопку "Пропустить".',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Пропустить"), KeyboardButton(text="Отмена")]
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(CreateTaskForm.notes, F.text)
async def get_task_notes_handler(message: types.Message, state: FSMContext):
    notes = message.md_text
    if notes == "Пропустить":
        notes = None
    await state.update_data(notes=notes)
    await state.set_state(CreateTaskForm.visible)
    await message.answer(
        "Ответ записан.\n\n"
        'Выберите, будет ли бот отображать задачу в общем списке задач? Выберите "Нет", если Вы добавляете задачу '
        "для использования её в соревновании. Тогда она будет доступна после того, как начнётся соревнование, в "
        "котором эта задача используется",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
                [KeyboardButton(text="Отмена")],
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(CreateTaskForm.visible, F.text.lower() == "да")
async def get_task_is_visible_yes_handler(message: types.Message, state: FSMContext):
    await state.update_data(visible=True)
    await lets_add_some_tests(message, state)


@form_router.message(CreateTaskForm.visible, F.text.lower() == "нет")
async def get_task_is_visible_no_handler(message: types.Message, state: FSMContext):
    await state.update_data(visible=False)
    await lets_add_some_tests(message, state)


@form_router.message(CreateTaskForm.visible)
async def get_task_is_visible_unknown_handler(message: types.Message):
    await message.reply(
        'Я Вас не понимаю. Пожалуйста, ответьте, стоит ли отображать задачу в общем списке задач? Отвечайте "Да" или '
        '"Нет", либо используйте клавиатуру для ответа. Если Вы хотите отменить создание задачи - напишите /cancel '
        'либо нажмите на кнопку "Отмена"'
    )


@form_router.message(CreateTaskForm.tests_in, F.text == "Хватит")
@form_router.message(CreateTaskForm.tests_out, F.text == "Хватит")
@form_router.message(CreateTaskForm.tests_visible, F.text == "Хватит")
async def stop_adding_task_tests_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if len(data["tests_visible"]) == 0:
        return await message.reply(
            "Вы не можете прекратить добавление тестов: необходимо добавить хотя бы один тест. Если Вы хотите "
            "отменить создание задачи, напишите /cancel."
        )

    await state.clear()
    user = db.get_user(telegram_id=message.from_user.id)
    task = Task(
        title=data["title"],
        description=data["description"],
        visible=data["visible"],
        notes=data["notes"],
        author_id=user.id,
    )
    with db.Session() as session:
        session.add(task)
        session.commit()
        session.refresh(task)

    os.mkdir(f"storage/tests/task_{task.id}_in")
    os.mkdir(f"storage/tests/task_{task.id}_out")
    for count, (test_in, test_out, test_visible) in enumerate(
        zip(data["tests_in"], data["tests_out"], data["tests_visible"]),
        start=1
    ):
        with open(
            f"storage/tests/task_{task.id}_in/{count}{'_example' if test_visible else ''}.txt",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(test_in)
        with open(
            f"storage/tests/task_{task.id}_out/{count}{'_example' if test_visible else ''}.txt",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(test_out)

    await message.reply(
        "Задача добавлена! Возвращаю за админ-панель",
        reply_markup=admin_panel_main_keyboard(
            user.can_create_tasks,
            user.can_create_contests,
            user.can_manage_permissions,
            user.is_owner,
        ),
    )
    if task.visible:
        with db.Session() as session:
            for user in session.scalars(
                select(
                    TgBotUser
                ).where(
                    TgBotUser.new_task_notifications_enabled == True
                )
            ):
                try:
                    await message.bot.send_message(
                        user.telegram_id,
                        f"Появилась новая задача: *{task.title}*",
                        parse_mode="MarkdownV2",
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="Открыть задачу",
                                        callback_data=f"tasks_list_{task.id}"
                                    )
                                ]
                            ]
                        )
                    )
                    await sleep(2)
                except exceptions.TelegramRetryAfter as ra:
                    await sleep(ra.retry_after)
                except:
                    pass


async def lets_add_some_tests(message: types.Message, state: FSMContext):
    await state.set_state(CreateTaskForm.tests_in)
    await state.update_data(tests_in=[], tests_out=[], tests_visible=[])
    await message.reply(
        "А теперь самое любимое: добавление тестов для задач. Бот будет запрашивать входные и выходные данные для "
        'теста, а также спрашивать, стоит ли показывать этот тест как пример, пока Вы не нажмёте кнопку "Хватит". '
        "Если же Вы хотите отменить создание задачи, используйте команду /cancel (кнопку отмены я убрал специально, "
        "чтобы Вы случайно не нажали на неё).\n\n"
        "Пожалуйста, введите входные данные для данного теста (можно отправить файлом с кодировкой UTF-8).",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Хватит")]], resize_keyboard=True
        ),
    )


@form_router.message(CreateTaskForm.tests_in, (F.text | F.document))
async def get_task_test_in_handler(message: types.Message, state: FSMContext):
    test_in = message.text
    if test_in is None:
        test_in = (
            (await message.bot.download(message.document.file_id))
            .read()
            .decode("utf-8")
        )
    tests_in = (await state.get_data())["tests_in"] + [test_in]
    await state.update_data(tests_in=tests_in)
    await state.set_state(CreateTaskForm.tests_out)
    await message.reply(
        "Хорошо, теперь пришлите выходные данные (можно отправить файлом с кодировкой UTF-8)"
    )


@form_router.message(CreateTaskForm.tests_out, (F.text | F.document))
async def get_task_test_out_handler(message: types.Message, state: FSMContext):
    test_out = message.text
    if test_out is None:
        test_out = (
            (await message.bot.download(message.document.file_id))
            .read()
            .decode("utf-8")
        )
    tests_out = (await state.get_data())["tests_out"] + [test_out]
    await state.update_data(tests_out=tests_out)
    await state.set_state(CreateTaskForm.tests_visible)
    await message.reply(
        "Прекрасно! Теперь укажите, стоит ли показывать этот тест пользователям?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
                [KeyboardButton(text="Хватит")],
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(CreateTaskForm.tests_visible)
async def get_task_test_visible_handler(message: types.Message, state: FSMContext):
    if message.text.lower() not in ["да", "нет"]:
        return await message.reply(
            "Я не понимаю Вас. Пожалуйста, выберите, нужно ли показывать данный тест пользователям?"
        )
    tests_visible = (await state.get_data())["tests_visible"] + [
        message.text.lower() == "да"
    ]
    await state.update_data(tests_visible=tests_visible)
    await state.set_state(CreateTaskForm.tests_in)
    await message.reply(
        "Тест добавлен. Теперь начинается добавление следующего теста.\n\n"
        "Пожалуйста, отправьте входные данные теста. Можно файлом в кодировке UTF-8.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Хватит")]], resize_keyboard=True
        ),
    )
