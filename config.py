import os

# Токен берется из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Установите переменную окружения BOT_TOKEN")

# Настройки баллов
MAX_SPEND_RUB_PER_CHECK = 200
BONUS_EXPIRE_DAYS = 180
REMIND_DAYS_BEFORE = 3
DEFAULT_CITY = "Москва"

# База данных
DATABASE_URL = os.getenv("DATABASE_URL", "")
