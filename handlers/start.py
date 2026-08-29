from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_user, user_exists
from keyboards.inline import main_menu_kb, register_kb, menu_kb, lifestyle_kb

router = Router()


class Registration(StatesGroup):
    name = State()
    age = State()
    lifestyle = State()
    current_weight = State()
    goal_weight = State()
    timeline = State()


async def _cleanup(message: Message, state: FSMContext, new_text: str, **kwargs):
    data = await state.get_data()
    prev_bot_msg_id = data.get("bot_msg_id")

    if prev_bot_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, prev_bot_msg_id)
        except Exception:
            pass

    try:
        await message.delete()
    except Exception:
        pass

    sent = await message.answer(new_text, **kwargs)
    await state.update_data(bot_msg_id=sent.message_id)


LIFESTYLE_MULTIPLIERS = {
    "sedentary": 22,
    "moderate": 25,
    "active": 28,
}


def _calc_calories(weight: float, goal: float, months: int, lifestyle: str) -> int:
    multiplier = LIFESTYLE_MULTIPLIERS.get(lifestyle, 25)
    maintenance = weight * multiplier
    kg_to_lose = weight - goal
    if kg_to_lose <= 0 or months <= 0:
        return int(maintenance)
    daily_deficit = (kg_to_lose * 7700) / (months * 30)
    calories = maintenance - daily_deficit
    return max(1200, int(calories))


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    if await user_exists(message.from_user.id):
        try:
            await message.delete()
        except Exception:
            pass
        sent = await message.answer(
            "🏠 <b>Главное меню</b>",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
        await state.update_data(bot_msg_id=sent.message_id)
        return

    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    prev_bot_msg_id = data.get("bot_msg_id")
    if prev_bot_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, prev_bot_msg_id)
        except Exception:
            pass

    sent = await message.answer(
        "🏋️ <b>Добро пожаловать в Weight Tracker!</b>\n\n"
        "Твой помощник в достижении идеального веса 💪\n\n"
        "Нажми кнопку ниже, чтобы начать 👇",
        reply_markup=register_kb(),
        parse_mode="HTML"
    )
    await state.update_data(bot_msg_id=sent.message_id)


@router.callback_query(F.data == "start_registration")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except Exception:
        pass

    sent = await callback.message.answer(
        "📝 Как тебя зовут?",
        parse_mode="HTML"
    )
    await state.update_data(bot_msg_id=sent.message_id)
    await state.set_state(Registration.name)
    await callback.answer()


@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 50:
        await _cleanup(message, state, "❌ Имя должно быть от 2 до 50 символов. Попробуй еще раз!")
        return

    await state.update_data(name=name)
    await _cleanup(
        message, state,
        f"🎉 Приятно познакомиться, <b>{name}</b>!\n\n"
        "📅 Сколько тебе лет?",
        parse_mode="HTML"
    )
    await state.set_state(Registration.age)


@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
    except ValueError:
        await _cleanup(message, state, "❌ Это не похоже на число. Попробуй еще раз!")
        return

    if age < 10 or age > 120:
        await _cleanup(message, state, "❌ Пожалуйста, введи корректный возраст (число от 10 до 120)")
        return

    await state.update_data(age=age)

    data = await state.get_data()
    prev_bot_msg_id = data.get("bot_msg_id")
    if prev_bot_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, prev_bot_msg_id)
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass

    sent = await message.answer(
        "🏃 Какой у тебя образ жизни?",
        reply_markup=lifestyle_kb(),
        parse_mode="HTML"
    )
    await state.update_data(bot_msg_id=sent.message_id)
    await state.set_state(Registration.lifestyle)


@router.callback_query(F.data.startswith("lifestyle_"), Registration.lifestyle)
async def process_lifestyle(callback: CallbackQuery, state: FSMContext):
    lifestyle = callback.data.replace("lifestyle_", "")
    await state.update_data(lifestyle=lifestyle)

    try:
        await callback.message.delete()
    except Exception:
        pass

    sent = await callback.message.answer("⚖️ Какой у тебя вес? (в кг)", parse_mode="HTML")
    await state.update_data(bot_msg_id=sent.message_id)
    await state.set_state(Registration.current_weight)
    await callback.answer()


@router.message(Registration.current_weight)
async def process_current_weight(message: Message, state: FSMContext):
    text = message.text.strip().replace(",", ".")
    try:
        weight = float(text)
    except ValueError:
        await _cleanup(message, state, "❌ Это не похоже на число. Попробуй еще раз!")
        return

    if weight < 20 or weight > 300:
        await _cleanup(message, state, "❌ Пожалуйста, введи корректный вес (число от 20 до 300 кг)")
        return

    await state.update_data(current_weight=weight)
    await _cleanup(message, state, "🎯 Какая цель веса? (в кг)")
    await state.set_state(Registration.goal_weight)


@router.message(Registration.goal_weight)
async def process_goal_weight(message: Message, state: FSMContext):
    text = message.text.strip().replace(",", ".")
    try:
        goal = float(text)
    except ValueError:
        await _cleanup(message, state, "❌ Это не похоже на число. Попробуй еще раз!")
        return

    if goal < 20 or goal > 300:
        await _cleanup(message, state, "❌ Пожалуйста, введи корректный вес (число от 20 до 300 кг)")
        return

    await state.update_data(goal_weight=goal)
    await _cleanup(message, state, "📅 За сколько месяцев ты хочешь достичь цели?")
    await state.set_state(Registration.timeline)


@router.message(Registration.timeline)
async def process_timeline(message: Message, state: FSMContext):
    try:
        months = int(message.text.strip())
    except ValueError:
        await _cleanup(message, state, "❌ Это не похоже на число. Попробуй еще раз!")
        return

    if months < 1 or months > 36:
        await _cleanup(message, state, "❌ Укажи от 1 до 36 месяцев")
        return

    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    current = data["current_weight"]
    goal = data["goal_weight"]
    lifestyle = data.get("lifestyle", "moderate")

    calories = _calc_calories(current, goal, months, lifestyle)

    await add_user(message.from_user.id, name, age, current, goal, lifestyle, months, calories)

    await _cleanup(
        message, state,
        "✅ <b>Регистрация завершена!</b>\n\n"
        "Добро пожаловать в Weight Tracker! 🎉\n"
        "Нажми кнопку ниже, чтобы открыть меню 👇",
        reply_markup=menu_kb(),
        parse_mode="HTML"
    )
    await state.clear()
