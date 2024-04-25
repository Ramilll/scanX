from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def on_start(message: types.Message):
    await message.answer(
        "Hello! I'm a bot that analyze Ethereum transactions and look for the most profitable ones."
    )
