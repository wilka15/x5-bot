import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Установите переменную окружения BOT_TOKEN")

MAX_SPEND_RUB_PER_CHECK = 20
BONUS_EXPIRE_DAYS = 180
REMIND_DAYS_BEFORE = 3
DEFAULT_CITY = "Москва"
DATABASE_URL = os.getenv("DATABASE_URL", "")
