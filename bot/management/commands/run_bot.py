import asyncio
import logging
from aiogram import Bot, Dispatcher
from django.core.management import BaseCommand

from bot.headers import router
from bot.management.commands.commands import commands

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_logs.txt"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def startup(bot: Bot):
    await bot.send_message(chat_id=5092869653, text='<b>Bot ishga tushdi✅</b>')


async def shutdown(bot: Bot):
    await bot.send_message(chat_id=5092869653, text='<b>Bot ishdan toxtadi🛑</b>')


async def main():
    print("Starting bot...")
    logging.basicConfig(level=logging.INFO)

    from bot.headers.handlers import bot
    dp = Dispatcher()
    await bot.set_my_commands(commands=commands)
    logger.info("Buyruqlar o'rnatildi.")
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_router(router)
    logger.info("Router ulandi.")
    await dp.start_polling(bot)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            asyncio.run(main())
        except Exception as e:
            logger.error(f"Bot ishga tushishda xatolik yuzz berdi {e}")
