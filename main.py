import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

import config
from app.handlers import router
from app.database.models import async_main

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="info", description="Информация о боте")
    ]
    await bot.set_my_commands(commands)

async def main():
    await async_main()  # Создание таблиц в базе данных
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await set_bot_commands(bot)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')

