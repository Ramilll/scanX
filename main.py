from bot.handlers.start import router as start_router
from bot.handlers.subscription import router as subscription_router
from bot.handlers.top import router as top_router
from bot.services.monitor import monitor_addresses

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from loguru import logger

from bot.config import Config

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    username = (await bot.get_me()).username
    logger.info(f"Bot https://t.me/{username} started")
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="subscribe", description="Subscribe to address"),
            BotCommand(command="unsubscribe", description="Unsubscribe from address"),
            BotCommand(command="top", description="Get top addresses"),
            BotCommand(command="my_subscriptions", description="Get your subscriptions"),
        ]
    )

    dp.include_routers(start_router, subscription_router, top_router)
    # And the run events dispatching
    await dp.start_polling(bot)
    
async def monitor():
    while True:
        logger.info("Monitoring addresses")
        await monitor_addresses()
        logger.info("Monitoring finished")
        await asyncio.sleep(60)
    
    


if __name__ == "__main__":
    import asyncio

    loop = asyncio.new_event_loop()
    
    loop.create_task(monitor())
    loop.run_until_complete(main())
