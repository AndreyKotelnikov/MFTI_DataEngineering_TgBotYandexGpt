from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
import app.keyboards as kb
from app.gpt import ask_yandex_gpt
from app.keyboards import inline_keyboard
from app.database.requests import set_user, update_user_name, update_user_sex, get_gpt_count, get_feedback_count, \
    get_gpt_messages
from app.middlewares import SaveHistoryMiddleware


router = Router()
router.message.outer_middleware(SaveHistoryMiddleware())
router.callback_query.outer_middleware(SaveHistoryMiddleware())


class Register(StatesGroup):
    name = State()
    sex = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await set_user(message.from_user)
    if user and user.name:
        await message.answer(f'С возвращением, {user.name}!')
        await message.answer('Перейдём сразу к общению с YandexGPT')
        await state.clear()
        return

    sent = await message.answer('Введите ваше имя')
    await state.set_state(Register.name)
    await state.update_data(question_msg_id=sent.message_id)


@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(method='register_name')
    # Если сообщение пустое, то снова просим указать имя
    if not message.text:
        await message.answer('Пожалуйста, введите ваше имя')
        return

    await update_user_name(message.text, message.from_user)

    data = await state.get_data()
    question_msg_id = data.get("question_msg_id")
    # Удаляем предыдущее сообщение с вопросом
    if question_msg_id:
        await message.bot.delete_message(message.chat.id, question_msg_id)
    # Сохраняем имя пользователя
    await state.update_data(name=message.text)
    # Удаляем текущее сообщение
    await message.bot.delete_message(message.chat.id, message.message_id)

    await state.set_state(Register.sex)
    # Отправляем следующий вопрос (с inline клавиатурой) и сохраняем его ID
    sent = await message.answer('Укажите ваш пол', reply_markup=inline_keyboard)
    await state.update_data(question_msg_id=sent.message_id)


@router.callback_query(Register.sex, F.data.in_(['man', 'woman', 'nice']))
async def register_sex(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data.get("name", "Пользователь")

    # Формируем сообщение на основе выбора
    if callback.data == 'man':
        alert_text = f'{name}, ты настоящий мужик!'
    elif callback.data == 'woman':
        alert_text = f'{name}, мой почтение, красавица!'
    else:
        alert_text = f'{name}, отличный выбор!'

    await update_user_sex(callback.data, callback.from_user)

    # Показываем всплывающее сообщение
    await callback.answer(alert_text)

    chat_id = callback.message.chat.id
    sent = await callback.message.answer('Удаление сообщений через 10 секунд...')

    # Симуляция анимации: обратный отсчёт с редактированием сообщения
    for i in range(10, 0, -1):
        try:
            await sent.edit_text(f'Удаление сообщений через {i}...')
            if i == 1:
                await callback.bot.delete_message(chat_id, sent.message_id)
                # Удаляем сообщение с вопросом, которое сохранили ранее
                question_msg_id = data.get("question_msg_id")
                if question_msg_id:
                    await callback.bot.delete_message(chat_id, question_msg_id)
        except Exception:
            pass
        await asyncio.sleep(0.5)

    # Очищаем состояние
    await state.clear()
    await state.update_data(method='register_sex')

    # Отправляем финальное сообщение
    await callback.message.answer(f'{name}, теперь можете пообщаться с YandexGPT')


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Расскажи боту что тебя беспокоит прямо сейчас!')


@router.message(Command('info'))
async def cmd_info(message: Message):
    await message.answer('Этот бот сделан для итогового проекта по дисциплине "Инжиниринг данных"!')

@router.message(F.text == 'Поблагодарить разработчика')
async def cmd_thanks(message: Message, state: FSMContext):
    await state.update_data(method='feedback')
    await message.answer('Спасибо за добрые слова!')

@router.message(F.text == 'Пожурить разработчика')
async def cmd_scold(message: Message, state: FSMContext):
    await state.update_data(method='feedback')
    await message.answer('Я всё исправлю!')

@router.message()
async def gpt(message: Message, state: FSMContext):
    await state.update_data(method='gpt')
    gpt_count = await get_gpt_count(message.from_user)
    reply_markup = None
    if 0 < gpt_count < 4:
        feedback_count = await get_feedback_count(message.from_user)
        if feedback_count == 0:
            reply_markup = kb.reply_keyboard

    context = await get_gpt_messages(message.from_user)
    result = await ask_yandex_gpt(message.text, context)
    if not result:
        result = "Произошла непредвиденная ошибка"
    elif len(result) > 4096:
        result = "Ответ слишком длинный, чтобы его отобразить."
    await message.answer(result, reply_markup=reply_markup, parse_mode='Markdown')
