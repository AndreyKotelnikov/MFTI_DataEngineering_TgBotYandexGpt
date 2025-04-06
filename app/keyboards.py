from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# Создание кнопок
thanks_btn = KeyboardButton(text='Поблагодарить разработчика')
scold_btn = KeyboardButton(text='Пожурить разработчика')

man_btn = InlineKeyboardButton(text='Мужской', callback_data='man')
woman_btn = InlineKeyboardButton(text='Женский', callback_data='woman')
nice_btn = InlineKeyboardButton(text='Хороший', callback_data='nice')

# Создание ReplyKeyboardMarkup
reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [thanks_btn],
        [scold_btn]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Дайте обратную связь по боту'
)
# Создание InlineKeyboardMarkup
inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [man_btn, woman_btn],
        [nice_btn]
    ]
)