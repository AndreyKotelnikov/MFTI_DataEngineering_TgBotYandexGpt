from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import datetime

from app.database.requests import add_user_history


class SaveHistoryMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: Dict[str, Any]
    ) -> Any:
        user_id = None
        event_type = None
        content = ""
        event_date = None
        user_db_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id
            event_date = event.date
            # Если текст начинается с '/', считаем, что это команда
            if event.text and event.text.startswith('/'):
                event_type = 'command'
            else:
                event_type = 'message'
            content = event.text or ""
            print(f"Saving {event_type} history: {content}")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            # Используем дату сообщения, к которому относится callback, либо текущее время
            event_date = event.message.date if event.message else datetime.datetime.utcnow()
            event_type = 'callback'
            content = event.data or ""
            print(f"Saving callback history: {content}")
        else:
            user_id = event.from_user.id if event.from_user else None
            event_date = datetime.datetime.utcnow()
            event_type = 'unknown'
            content = str(event)

        result = await handler(event, data)

        state: FSMContext = data.get('state')
        if state:
            state_data = await state.get_data()
            method_name = state_data.get('method')
            if method_name:
                event_type = method_name
                await state.update_data(method=None)

        if user_id is not None:
            await add_user_history(user_id, event_type, content, event_date)

        print(f"User ID: {user_id}, Event Type: {event_type}, Content: {content}, Date: {event_date}")

        return result
