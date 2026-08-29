import random
from typing import List
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db import (
    get_notification, init_notification, update_notification, get_user,
)
from keyboards.inline import (
    notifications_kb, notif_settings_kb,
    morning_time_kb, evening_time_kb,
    answer_kb, finish_kb,
    MORNING_QUESTIONS, EVENING_QUESTIONS,
)

router = Router()

WORKOUTS = [
    {
        "name": "Базовая",
        "emoji": "🏋️",
        "circles": 3,
        "exercises": [
            "Приседания — 15",
            "Ягодичный мостик — 15",
            "Отжимания от колен — 10",
            "Планка — 30 сек",
            "Велосипед лёжа — 20",
        ],
    },
    {
        "name": "Жиросжигание",
        "emoji": "🔥",
        "circles": 4,
        "exercises": [
            "Ходьба с подниманием колен — 1 мин",
            "Приседания — 12",
            "Альпинист — 20",
            "Ягодичный мостик — 15",
            "Планка — 30 сек",
        ],
    },
    {
        "name": "Кор и живот",
        "emoji": "🎯",
        "circles": 3,
        "exercises": [
            "Скручивания — 15",
            "Велосипед — 20",
            "Подъём таза лёжа — 15",
            "Планка — 40 сек",
            "Планка с касанием плеч — 10",
        ],
    },
    {
        "name": "Ноги и ягодицы",
        "emoji": "🦵",
        "circles": 4,
        "exercises": [
            "Приседания — 15",
            "Выпады назад — 10 на ногу",
            "Ягодичный мостик — 20",
            "Удержание приседа у стены — 30 сек",
            "Подъём на носки — 20",
        ],
    },
    {
        "name": "Верх тела",
        "emoji": "💪",
        "circles": 3,
        "exercises": [
            "Отжимания от колен — 10",
            "Планка — 40 сек",
            "Супермен — 15",
            "Обратные снежные ангелы — 15",
            "Боковая планка — 20 сек/сторону",
        ],
    },
    {
        "name": "Интервальная",
        "emoji": "⚡",
        "circles": 4,
        "exercises": [
            "Шаги на месте с руками вверх",
            "Приседания",
            "Альпинист",
            "Велосипед",
            "Планка",
        ],
        "note": "40 сек работа / 20 сек отдых",
    },
    {
        "name": "Полное тело",
        "emoji": "🏃",
        "circles": 3,
        "exercises": [
            "Приседания — 15",
            "Отжимания от колен — 10",
            "Ягодичный мостик — 15",
            "Велосипед — 20",
            "Планка — 30 сек",
            "Супермен — 15",
        ],
    },
    {
        "name": "Восстановительная",
        "emoji": "🧘",
        "circles": 2,
        "exercises": [
            "Кошка-корова — 10",
            "Ягодичный мостик — 15",
            "Скручивания — 10",
            "Планка — 20 сек",
            "Супермен — 10",
            "Медленные приседания — 10",
        ],
        "note": "Когда тяжело или болят мышцы",
    },
]


def format_workout(workout: dict) -> str:
    exercises = "\n".join(f"  {i+1}. {e}" for i, e in enumerate(workout["exercises"]))
    note = f"\n\n💡 {workout['note']}" if workout.get("note") else ""
    return (
        f"{workout['emoji']} <b>{workout['name']}</b>\n"
        f"🔄 Кругов: {workout['circles']}\n\n"
        f"{exercises}{note}"
    )


def _get_active_questions(notif: dict, ntype: str) -> List[str]:
    questions = MORNING_QUESTIONS if ntype == "morning" else EVENING_QUESTIONS
    keys = []
    for q_key in questions:
        if notif[q_key]:
            keys.append(q_key)
    return keys


def _get_question_text(ntype: str, q_key: str, calories: int = 0) -> str:
    questions = MORNING_QUESTIONS if ntype == "morning" else EVENING_QUESTIONS
    text = questions[q_key]
    if ntype == "evening" and q_key == "q1" and calories:
        text = f"🍽 Вписался в норму калорий ({calories})?"
    return text


def _get_result(total: int, score: int) -> str:
    ratio = score / total if total > 0 else 0
    if ratio == 1.0:
        comment = "🏆 Идеальный день! Машина! 💪🔥"
    elif ratio >= 0.66:
        comment = "👏 Почти идеально! Отлично!"
    elif ratio >= 0.5:
        comment = "😊 Неплохо, продолжай! 🚀"
    elif ratio >= 0.33:
        comment = "😐 Могло быть лучше"
    else:
        comment = "😔 Слабый день, не сдавайся!"
    return f"<b>{score}/{total}</b>\n{comment}"


@router.callback_query(F.data == "notifications")
async def show_notifications(callback: CallbackQuery):
    await init_notification(callback.from_user.id)
    morning = await get_notification(callback.from_user.id, "morning")
    evening = await get_notification(callback.from_user.id, "evening")

    await callback.message.edit_text(
        "🔔 <b>Настройка оповещений</b>",
        reply_markup=notifications_kb(morning, evening),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "notif_morning")
async def show_morning(callback: CallbackQuery):
    notif = await get_notification(callback.from_user.id, "morning")
    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        "☀️ <b>Утренние оповещения</b>",
        reply_markup=notif_settings_kb("morning", notif, user),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "notif_evening")
async def show_evening(callback: CallbackQuery):
    notif = await get_notification(callback.from_user.id, "evening")
    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        "🌙 <b>Вечерние оповещения</b>",
        reply_markup=notif_settings_kb("evening", notif, user),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "notif_back_main")
async def back_to_notif_main(callback: CallbackQuery):
    morning = await get_notification(callback.from_user.id, "morning")
    evening = await get_notification(callback.from_user.id, "evening")
    await callback.message.edit_text(
        "🔔 <b>Настройка оповещений</b>",
        reply_markup=notifications_kb(morning, evening),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("notif_toggle_"))
async def toggle_notif(callback: CallbackQuery):
    ntype = callback.data.replace("notif_toggle_", "")
    if ntype in ("morning", "evening"):
        notif = await get_notification(callback.from_user.id, ntype)
        user = await get_user(callback.from_user.id)
        new_val = 0 if notif["enabled"] else 1
        await update_notification(callback.from_user.id, ntype, enabled=new_val)
        notif = await get_notification(callback.from_user.id, ntype)
        await callback.message.edit_reply_markup(reply_markup=notif_settings_kb(ntype, notif, user))
        status = "включены" if new_val else "выключены"
        await callback.answer(f"Оповещения {status} ✅")


@router.callback_query(F.data.startswith("notif_time_"))
async def show_time(callback: CallbackQuery):
    ntype = callback.data.replace("notif_time_", "")
    if ntype == "morning":
        await callback.message.edit_text("☀️ Выбери время (МСК):", reply_markup=morning_time_kb(), parse_mode="HTML")
    else:
        await callback.message.edit_text("🌙 Выбери время (МСК):", reply_markup=evening_time_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("notif_settime_"))
async def save_time(callback: CallbackQuery):
    parts = callback.data.split("_")
    ntype = parts[2]
    hour = int(parts[3])
    await update_notification(callback.from_user.id, ntype, hour=hour)
    notif = await get_notification(callback.from_user.id, ntype)
    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"{'☀️' if ntype == 'morning' else '🌙'} <b>{'Утренние' if ntype == 'morning' else 'Вечерние'} оповещения</b>",
        reply_markup=notif_settings_kb(ntype, notif, user),
        parse_mode="HTML"
    )
    await callback.answer(f"Время: {hour:02d}:00 ✅")


@router.callback_query(F.data.startswith("notif_q_"))
async def toggle_question(callback: CallbackQuery):
    parts = callback.data.split("_")
    ntype = parts[2]
    q_key = parts[3]
    notif = await get_notification(callback.from_user.id, ntype)
    new_val = 0 if notif[q_key] else 1
    await update_notification(callback.from_user.id, ntype, **{q_key: new_val})
    notif = await get_notification(callback.from_user.id, ntype)
    user = await get_user(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=notif_settings_kb(ntype, notif, user))
    await callback.answer()


@router.callback_query(F.data == "notif_test")
async def test_notification(callback: CallbackQuery):
    morning = await get_notification(callback.from_user.id, "morning")
    evening = await get_notification(callback.from_user.id, "evening")

    await callback.message.edit_text(
        "🧪 <b>Тест</b>\n\nКакое оповещение отправить?",
        reply_markup=CallbackKeyboard("notif_test_morning", "notif_test_evening"),
        parse_mode="HTML"
    )
    await callback.answer()


def CallbackKeyboard(cb1: str, cb2: str):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☀️ Утреннее", callback_data=cb1)],
        [InlineKeyboardButton(text="🌙 Вечернее", callback_data=cb2)],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="notif_back_main")],
    ])


@router.callback_query(F.data.startswith("notif_test_"))
async def send_test(callback: CallbackQuery):
    ntype = callback.data.replace("notif_test_", "")
    notif = await get_notification(callback.from_user.id, ntype)
    questions = _get_active_questions(notif, ntype)

    if not questions:
        await callback.answer("Нет активных пунктов!", show_alert=True)
        return

    user = await get_user(callback.from_user.id)
    calories = user["daily_calories"] if user else 2000
    workout = format_workout(random.choice(WORKOUTS))
    total = len(questions)
    first_key = questions[0]

    label = "Утреннее" if ntype == "morning" else "Вечернее"
    q_text = _get_question_text(ntype, first_key, calories)

    text = f"📢 <b>{label} оповещение</b>\n\n{q_text}"
    if ntype == "morning" and first_key == "q3":
        text += f"\n\n🏋️ Тренировка на сегодня:\n{workout}"

    await callback.message.answer(
        text, parse_mode="HTML",
        reply_markup=answer_kb(ntype, first_key, total, 0, 0, calories)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ans_"))
async def handle_answer(callback: CallbackQuery):
    data = callback.data

    if data == "ans_finish":
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.answer()
        return

    parts = data.split("_")
    ntype = parts[1]
    question_key = parts[2]
    answer = parts[3]
    total = int(parts[4])
    score = int(parts[5])
    idx = int(parts[6])

    if answer == "yes":
        score += 1

    try:
        await callback.message.delete()
    except Exception:
        pass

    notif = await get_notification(callback.from_user.id, ntype)
    questions = _get_active_questions(notif, ntype)
    user = await get_user(callback.from_user.id)
    calories = user["daily_calories"] if user else 2000
    workout = format_workout(random.choice(WORKOUTS))
    label = "Утреннее" if ntype == "morning" else "Вечернее"

    next_idx = idx + 1

    if next_idx < total:
        next_key = questions[next_idx]
        q_text = _get_question_text(ntype, next_key, calories)
        text = f"📢 <b>{label} оповещение</b>\n\n{q_text}"
        if ntype == "morning" and next_key == "q3":
            text += f"\n\n🏋️ Тренировка на сегодня:\n{workout}"
        await callback.message.answer(
            text, parse_mode="HTML",
            reply_markup=answer_kb(ntype, next_key, total, score, next_idx, calories)
        )
    else:
        result = _get_result(total, score)
        await callback.message.answer(result, parse_mode="HTML", reply_markup=finish_kb())

    await callback.answer()


async def send_daily_notification(bot, user_id: int, ntype: str):
    notif = await get_notification(user_id, ntype)
    if not notif:
        return

    questions = _get_active_questions(notif, ntype)
    if not questions:
        return

    user = await get_user(user_id)
    calories = user["daily_calories"] if user else 2000
    workout = format_workout(random.choice(WORKOUTS))
    total = len(questions)
    first_key = questions[0]
    label = "Утреннее" if ntype == "morning" else "Вечернее"
    q_text = _get_question_text(ntype, first_key, calories)

    text = f"📢 <b>{label} оповещение</b>\n\n{q_text}"
    if ntype == "morning" and first_key == "q3":
        text += f"\n\n🏋️ Тренировка на сегодня:\n{workout}"

    await bot.send_message(
        user_id, text, parse_mode="HTML",
        reply_markup=answer_kb(ntype, first_key, total, 0, 0, calories)
    )
