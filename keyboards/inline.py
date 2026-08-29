from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Регистрация", callback_data="start_registration")],
    ])


def menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Меню", callback_data="back_to_menu")],
    ])


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton(text="⚖️ Взвеситься", callback_data="weigh")],
        [InlineKeyboardButton(text="🔔 Оповещения", callback_data="notifications")],
    ])


def profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить профиль", callback_data="delete_profile")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ])


def confirm_delete_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete"),
            InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete"),
        ],
    ])


def notifications_kb(morning: dict, evening: dict) -> InlineKeyboardMarkup:
    m_status = "✅" if morning["enabled"] else "❌"
    e_status = "✅" if evening["enabled"] else "❌"
    m_time = f"{morning['hour']:02d}:00"
    e_time = f"{evening['hour']:02d}:00"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"☀️ Утро ({m_time}) {m_status}", callback_data="notif_morning")],
        [InlineKeyboardButton(text=f"🌙 Вечер ({e_time}) {e_status}", callback_data="notif_evening")],
        [InlineKeyboardButton(text="🧪 Тест", callback_data="notif_test")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ])


MORNING_QUESTIONS = {
    "q1": "💊 Выпил витамины?",
    "q2": "🧘 Воздержался?",
    "q3": "💪 Сделал зарядку?",
}

EVENING_QUESTIONS = {
    "q1": "🍽 Вписался в норму калорий?",
    "q2": "🥗 Хорошо питался?",
    "q3": "🚶 Прошёл достаточно шагов?",
}


def lifestyle_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛋 Малоподвижный", callback_data="lifestyle_sedentary")],
        [InlineKeyboardButton(text="🚶 Средний", callback_data="lifestyle_moderate")],
        [InlineKeyboardButton(text="🏃 Подвижный", callback_data="lifestyle_active")],
    ])


def notif_settings_kb(ntype: str, notif: dict, user: dict = None) -> InlineKeyboardMarkup:
    questions = MORNING_QUESTIONS if ntype == "morning" else EVENING_QUESTIONS
    icon = lambda v: "✅" if v else "❌"
    time_str = f"{notif['hour']:02d}:00"
    status = "Вкл ✅" if notif["enabled"] else "Выкл ❌"
    calories = user["daily_calories"] if user else 2000
    q1_text = questions["q1"]
    if ntype == "evening" and "калорий" in q1_text:
        q1_text = f"🍽 Вписался в норму калорий ({calories})?"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⏰ {time_str}", callback_data=f"notif_time_{ntype}")],
        [InlineKeyboardButton(text=f"🔔 {status}", callback_data=f"notif_toggle_{ntype}")],
        [InlineKeyboardButton(text=f"{q1_text} {icon(notif['q1'])}", callback_data=f"notif_q_{ntype}_q1")],
        [InlineKeyboardButton(text=f"{questions['q2']} {icon(notif['q2'])}", callback_data=f"notif_q_{ntype}_q2")],
        [InlineKeyboardButton(text=f"{questions['q3']} {icon(notif['q3'])}", callback_data=f"notif_q_{ntype}_q3")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="notif_back_main")],
    ])


def morning_time_kb() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=f"{h:02d}:00", callback_data=f"notif_settime_morning_{h}") for h in [5, 8, 11]]
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="🔙 Назад", callback_data="notif_morning")],
    ])


def evening_time_kb() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=f"{h:02d}:00", callback_data=f"notif_settime_evening_{h}") for h in [18, 21, 0]]
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="🔙 Назад", callback_data="notif_evening")],
    ])


def answer_kb(ntype: str, question: str, total: int, score: int, idx: int, calories: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"ans_{ntype}_{question}_yes_{total}_{score}_{idx}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"ans_{ntype}_{question}_no_{total}_{score}_{idx}"),
        ],
    ])


def finish_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Завершить", callback_data="ans_finish")],
    ])
