from datetime import datetime, timedelta

from app.database.models import async_session
from app.database.models import User, UserHistory
from sqlalchemy import select, update, func
from aiogram.types import DateTime
from aiogram.types.user import User as TgUser


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper


@connection
async def set_user(session, user: TgUser):
    user_db = await session.scalar(select(User).where(User.telegram_id == user.id))
    if not user_db:
        session.add(User(telegram_id=user.id, username=user.username, first_name=user.first_name, last_name=user.last_name))
        await session.commit()
        return False
    else:
        return user_db

@connection
async def update_user_name(session, name: str, user: TgUser):
    await session.execute(update(User).where(User.telegram_id == user.id).values(name=name))
    await session.commit()

@connection
async def update_user_sex(session, sex: str, user: TgUser):
    await session.execute(update(User).where(User.telegram_id == user.id).values(sex=sex))
    await session.commit()

@connection
async def add_user_history(session, telegram_id: int, action: str, message: str, date: DateTime):
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user:
        session.add(UserHistory(user_id=user.id, action=action, message=message, date_time=date))
        await session.commit()
        return True
    return False

@connection
async def get_gpt_count(session, user: TgUser):
    # Получаем у пользователя количество записей из UserHistory, где action = 'gpt'
    count = await session.scalar(
        select(func.count())
        .select_from(UserHistory)
        .join(User, User.id == UserHistory.user_id)
        .where(User.telegram_id == user.id, UserHistory.action == 'gpt')
    )
    return count

@connection
async def get_feedback_count(session, user: TgUser):
    # Получаем у пользователя количество записей из UserHistory, где action = 'feedback'
    count = await session.scalar(
        select(func.count())
        .select_from(UserHistory)
        .join(User, User.id == UserHistory.user_id)
        .where(User.telegram_id == user.id, UserHistory.action == 'feedback')
    )
    return count

@connection
async def get_gpt_messages(session, user: TgUser):
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    stmt = (
        select(UserHistory.message)
        .select_from(UserHistory)
        .join(User, User.id == UserHistory.user_id)
        .where(
            User.telegram_id == user.id,
            UserHistory.action == 'gpt',
            UserHistory.date_time >= time_threshold
        )
    )
    result = await session.scalars(stmt)
    return result.all()