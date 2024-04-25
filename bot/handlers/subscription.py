from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import re
from db import Database

router = Router()
database = Database()

address_pattern = re.compile(r"0x[a-fA-F0-9]{40}")  # Ethereum address pattern
cancel_keyboard = InlineKeyboardBuilder(
    [[types.InlineKeyboardButton(text="Cancel", callback_data="cancel")]]
).as_markup()


@router.message(Command("subscribe"))
async def on_subscribe(message: types.Message, context: FSMContext):
    await message.answer(
        "Enter the address you want to subscribe to.", reply_markup=cancel_keyboard
    )
    await context.set_state("subscribe:address")


@router.message(state="subscribe:address")
async def on_subscribe_address(message: types.Message, context: FSMContext):
    if not message.text:
        return
    address = message.text

    if not address_pattern.match(address):
        await message.answer(
            "Invalid address. Please try again.", reply_markup=cancel_keyboard
        )
        return

    with database as db:
        if db.is_subscribed(str(message.chat.id), address):
            await message.answer("You are already subscribed to this address.")
            await context.clear()
            return

    await context.update_data(address=address)

    with database as db:
        db.add_subscription(str(message.chat.id), address)
        db.session.commit()

    await message.answer(
        f"Subscribed to <code>{address}</code>. You will receive notifications about new transactions.",
        parse_mode="HTML",
    )
    await context.clear()
    

@router.message(Command("unsubscribe"))
async def on_unsubscribe(message: types.Message, context: FSMContext):
    await message.answer(
        "Enter the address you want to unsubscribe from.", reply_markup=cancel_keyboard
    )
    await context.set_state("unsubscribe:address")
    
@router.message(state="unsubscribe:address")
async def on_unsubscribe_address(message: types.Message, context: FSMContext):
    if not message.text:
        return
    address = message.text

    if not address_pattern.match(address):
        await message.answer(
            "Invalid address. Please try again.", reply_markup=cancel_keyboard
        )
        return

    with database as db:
        if not db.is_subscribed(str(message.chat.id), address):
            await message.answer("You are not subscribed to this address.")
            await context.clear()
            return

    await context.update_data(address=address)

    with database as db:
        db.remove_subscription(str(message.chat.id), address)
        db.session.commit()

    await message.answer(
        f"Unsubscribed from <code>{address}</code>. You will no longer receive notifications about new transactions.",
        parse_mode="HTML",
    )
    await context.clear()


@router.callback_query(F.data == "cancel", state="*")
async def on_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    assert isinstance(callback_query.message, types.Message)  # for type checker

    await callback_query.message.answer("Cancelled.")
    await state.clear()


@router.message(Command("my_subscriptions"))
async def on_subscriptions(message: types.Message):
    with database as db:
        subscriptions = db.get_subscriptions_by_user_id(str(message.chat.id))

    if not subscriptions:
        await message.answer("You are not subscribed to any addresses.")
        return

    text = "Your subscriptions:\n"
    for subscription in subscriptions:
        text += f"- <code>{subscription.address}</code>\n"

    await message.answer(text, parse_mode="HTML")