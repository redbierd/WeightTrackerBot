import asyncio
import os
import logging
from datetime import datetime, timezone, timedelta
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database.db import init_db, get_active_notifications
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.notification import router as notification_router, send_daily_notification

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN", "")
MOSCOW_OFFSET = 3


async def scheduler(bot: Bot):
    while True:
        try:
            now = datetime.now(timezone(timedelta(hours=MOSCOW_OFFSET)))
            moscow_hour = now.hour
            moscow_minute = now.minute

            if moscow_minute == 0:
                notifications = await get_active_notifications(moscow_hour, moscow_minute)
                for notif in notifications:
                    try:
                        await send_daily_notification(bot, notif["user_id"], notif["type"])
                    except Exception as e:
                        logging.error(f"Ошибка отправки оповещения: {e}")
        except Exception as e:
            logging.error(f"Ошибка планировщика: {e}")

        await asyncio.sleep(60)


async def main():
    if not TOKEN:
        logging.error("BOT_TOKEN не задан! Укажи переменную окружения BOT_TOKEN")
        return

    await init_db()
    logging.info("База данных инициализирована")

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(notification_router)

    asyncio.create_task(scheduler(bot))
    logging.info("Планировщик оповещений запущен")
    logging.info("Бот запущен!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
