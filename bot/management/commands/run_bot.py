import asyncio
import logging

from django.core.management import BaseCommand

from bot.management.commands.commands import commands


async def main():
    print("Starting bot...")
    logging.basicConfig(level=logging.INFO)

    from bot.handlers import dp
    from bot.handlers import bot
    await bot.set_my_commands(commands=commands)
    await dp.start_polling(bot)


class Command(BaseCommand):
    def handle(self, *args, **options):
        asyncio.run(main())
