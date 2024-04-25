from aiogram import Router, types
from aiogram.filters import Command
from bot.services.get_top import get_top_addresses
from cachetools import TTLCache, cached  # type: ignore
from bot.services.get_top import AddressMetric

router = Router()


@cached(cache=TTLCache(maxsize=1, ttl=60))  # 1 minute cache
def request_top(top: int = 50) -> list["AddressMetric"]:
    return get_top_addresses(top)


@router.message(Command("top"))
async def on_top(message: types.Message):
    top = request_top(10)
    text = "Top 10 addresses by number of swap transactions:\n"
    for i, address in enumerate(top, 1):
        text += f"{i}. <code>{address}</code>\n"
    await message.answer(text, parse_mode="HTML")
