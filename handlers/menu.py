from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_user, delete_user, update_weight
from keyboards.inline import main_menu_kb, profile_kb, confirm_delete_kb

router = Router()


class WeighIn(StatesGroup):
    weight = State()


def _progress_bar(start: float, current: float, goal: float) -> str:
    total_to_lose = start - goal
    if total_to_lose <= 0:
        return "⚪ Нет цели"
    lost = start - current
    percent = max(0, min(100, int(lost / total_to_lose * 100)))
    filled = percent // 10
    bar = "🟩" * filled + "⬜" * (10 - filled)
    return f"{bar} {percent}%"


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)

    if not user:
        await callback.answer("Профиль не найден. Нажми /start", show_alert=True)
        return

    diff = round(user["current_weight"] - user["goal_weight"], 1)
    diff_text = f"{diff} кг" if diff > 0 else "Цель достигнута! 🎉"
    progress = _progress_bar(user["start_weight"], user["current_weight"], user["goal_weight"])

    await callback.message.edit_text(
        "👤 <b>Твой профиль</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📛 Имя: <b>{user['name']}</b>\n"
        f"📅 Возраст: <b>{user['age']}</b>\n"
        f"⚖️ Текущий вес: <b>{user['current_weight']} кг</b>\n"
        f"🎯 Цель: <b>{user['goal_weight']} кг</b>\n"
        f"📉 До цели: <b>{diff_text}</b>\n"
        f"🍽 Норма калорий: <b>{user['daily_calories']} ккал</b>\n"
        f"📆 Дата регистрации: <b>{user['registered_at']}</b>\n\n"
        f"📊 Прогресс:\n{progress}\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=profile_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "weigh")
async def weigh_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚖️ <b>Взвешивание</b>\n\n"
        "Введи свой текущий вес (в кг):",
        parse_mode="HTML"
    )
    await state.update_data(prompt_msg_id=callback.message.message_id)
    await state.set_state(WeighIn.weight)
    await callback.answer()


@router.message(WeighIn.weight)
async def process_weigh(message: Message, state: FSMContext):
    text = message.text.strip().replace(",", ".")
    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")

    try:
        await message.delete()
    except Exception:
        pass
    if prompt_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_msg_id)
        except Exception:
            pass

    try:
        weight = float(text)
    except ValueError:
        sent = await message.answer("❌ Это не похоже на число. Попробуй еще раз!")
        await state.update_data(prompt_msg_id=sent.message_id)
        return

    if weight < 20 or weight > 300:
        sent = await message.answer("❌ Пожалуйста, введи корректный вес (от 20 до 300 кг)")
        await state.update_data(prompt_msg_id=sent.message_id)
        return

    await update_weight(message.from_user.id, weight)
    user = await get_user(message.from_user.id)

    diff = round(weight - user["goal_weight"], 1)
    diff_text = f"{diff} кг" if diff > 0 else "Цель достигнута! 🎉"
    progress = _progress_bar(user["start_weight"], weight, user["goal_weight"])

    sent = await message.answer(
        f"✅ <b>Вес записан: {weight} кг</b>\n\n"
        f"📉 До цели: <b>{diff_text}</b>\n\n"
        f"📊 Прогресс:\n{progress}",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await state.update_data(bot_msg_id=sent.message_id)
    await state.clear()


@router.callback_query(F.data == "delete_profile")
async def delete_profile_prompt(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚠️ <b>Удаление профиля</b>\n\n"
        "Ты уверен, что хочешь удалить профиль?\n"
        "Все данные будут удалены безвозвратно.",
        reply_markup=confirm_delete_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден. Нажми /start", show_alert=True)
        return

    diff = round(user["current_weight"] - user["goal_weight"], 1)
    diff_text = f"{diff} кг" if diff > 0 else "Цель достигнута! 🎉"
    progress = _progress_bar(user["start_weight"], user["current_weight"], user["goal_weight"])

    await callback.message.edit_text(
        "👤 <b>Твой профиль</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📛 Имя: <b>{user['name']}</b>\n"
        f"📅 Возраст: <b>{user['age']}</b>\n"
        f"⚖️ Текущий вес: <b>{user['current_weight']} кг</b>\n"
        f"🎯 Цель: <b>{user['goal_weight']} кг</b>\n"
        f"📉 До цели: <b>{diff_text}</b>\n"
        f"🍽 Норма калорий: <b>{user['daily_calories']} ккал</b>\n"
        f"📆 Дата регистрации: <b>{user['registered_at']}</b>\n\n"
        f"📊 Прогресс:\n{progress}\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=profile_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_delete")
async def confirm_delete(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    current_msg_id = callback.message.message_id

    await delete_user(callback.from_user.id)
    await state.clear()

    for msg_id in range(current_msg_id, current_msg_id - 100, -1):
        try:
            await callback.bot.delete_message(chat_id, msg_id)
        except Exception:
            pass

    sent = await callback.message.answer(
        "👋 <b>Профиль удалён.</b>\n\n"
        "Все данные стерты. Если захочешь вернуться — нажми /start",
        parse_mode="HTML"
    )
    await state.update_data(bot_msg_id=sent.message_id)
