import asyncio
import sys
import logging
from datetime import datetime

# ====== ФИКС ДЛЯ WINDOWS (для совместимости) ======
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# ====== ИМПОРТЫ ======
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError

# Наши модули
from config import BOT_TOKEN, REMIND_DAYS_BEFORE, MAX_SPEND_RUB_PER_CHECK
from database import init_db, get_user, set_balance, set_city, set_notify
from recommend import recommend_products
from scheduler import init_scheduler

# ====== НАСТРОЙКА ЛОГИРОВАНИЯ ======
logging.basicConfig(level=logging.INFO)

# ====== СОЗДАНИЕ СЕССИИ (УПРОЩЁННО) ======
session = AiohttpSession()

# ====== ИНИЦИАЛИЗАЦИЯ БОТА ======
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

# ====== ОБРАБОТЧИКИ КОМАНД ======

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        "🍊 Привет! Я твой помощник по апельсинкам.\n\n"
        "Я помогу тебе:\n"
        "• Не забывать о сгорании баллов (напомню за 3 дня)\n"
        "• Подобрать товары, которые можно купить на баллы\n"
        "• Узнавать актуальные цены и акции в твоём городе\n\n"
        "Для начала отправь свой баланс:\n"
        "/balance 1500\n"
        "И установи свой город:\n"
        "/set_city Москва"
    )
    await message.answer(text)

@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Напиши число, например: /balance 1500")
            return
        balance = int(parts[1])
        if balance < 0:
            await message.answer("❌ Баланс не может быть отрицательным")
            return
        set_balance(message.from_user.id, balance)
        rub = balance // 10
        await message.answer(
            f"✅ Принято! {balance} баллов = {rub} руб.\n"
            f"Баллы сгорят через 180 дней.\n"
            f"Я напомню за {REMIND_DAYS_BEFORE} дня до сгорания."
        )
    except ValueError:
        await message.answer("❌ Это не число. Напиши: /balance 1500")

@dp.message(Command("set_city"))
async def cmd_set_city(message: types.Message):
    city = message.text.replace("/set_city", "").strip()
    if not city:
        await message.answer("❌ Укажите город, например: /set_city Москва")
        return
    set_city(message.from_user.id, city)
    await message.answer(f"✅ Город сохранён: {city}. Теперь я буду показывать цены для этого города.")

@dp.message(Command("recommend"))
async def cmd_recommend(message: types.Message):
    user_data = get_user(message.from_user.id)
    if not user_data or user_data["balance"] <= 0:
        await message.answer("❌ Сначала укажи свой баланс командой /balance")
        return

    balance = user_data["balance"]
    result = recommend_products(balance)

    product_list = "\n".join([f"• {p['name']} — {p['price']} руб" for p in result["products"]])
    text = (
        f"🍊 У вас {balance} баллов ({balance//10} руб.)\n"
        f"⚠️ За 1 раз можно списать максимум {MAX_SPEND_RUB_PER_CHECK} руб. (200 баллов)\n\n"
        f"🛒 Рекомендую взять:\n{product_list}\n"
        f"💰 Итого: {result['total_price']} руб.\n"
        f"💳 Баллами спишется: {result['spend_rub']} руб. ({result['spend_balls']} баллов)\n"
        f"💵 Вам останется заплатить: {result['user_pays']} руб.\n"
    )
    if result["remaining_balls"] > 0:
        text += f"\n❗ Остаток баллов после списания: {result['remaining_balls']} баллов ({result['remaining_balls']//10} руб.)"
        text += f"\nВы сможете потратить их за несколько походов в магазин."
    await message.answer(text)

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    user_data = get_user(message.from_user.id)
    if not user_data:
        await message.answer("❌ Ты еще не ввел баланс. Отправь /balance")
        return
    balance = user_data["balance"]
    rub = balance // 10
    expire_date = user_data["expire_date"]
    if expire_date:
        expire_dt = datetime.fromisoformat(expire_date)
        days_left = max(0, (expire_dt - datetime.now()).days)
        expire_str = expire_dt.strftime('%d.%m.%Y')
    else:
        days_left = "неизвестно"
        expire_str = "неизвестно"
    city = user_data.get("city") or "не указан"
    store = user_data.get("store_address") or "не указан"
    text = (
        f"🍊 Твой баланс: {balance} баллов ({rub} руб.)\n"
        f"📅 Сгорают: {expire_str}\n"
        f"⏳ Осталось дней: {days_left}\n"
        f"🏙 Город: {city}\n"
        f"🏪 Магазин: {store}\n"
        f"🔔 Уведомления: {'включены' if user_data['notify_enabled'] else 'выключены'}"
    )
    await message.answer(text)

@dp.message(Command("notify_on"))
async def cmd_notify_on(message: types.Message):
    set_notify(message.from_user.id, True)
    await message.answer("✅ Уведомления о сгорании включены!")

@dp.message(Command("notify_off"))
async def cmd_notify_off(message: types.Message):
    set_notify(message.from_user.id, False)
    await message.answer("🔕 Уведомления о сгорании выключены.")

@dp.message()
async def unknown_command(message: types.Message):
    await message.answer(
        "🤔 Я не знаю такой команды.\n"
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/balance <число> — установить баланс\n"
        "/set_city <город> — выбрать город\n"
        "/recommend — подобрать товары под баллы\n"
        "/check — проверить баланс и дату сгорания\n"
        "/notify_on / notify_off — включить/выключить напоминания"
    )

# ====== ЗАПУСК ======
async def main():
    init_db()
    logging.info("Бот запущен!")
    init_scheduler(bot)
    while True:
        try:
            await dp.start_polling(bot)
        except TelegramNetworkError as e:
            logging.error(f"Ошибка сети: {e}. Переподключение через 10 секунд...")
            await asyncio.sleep(10)
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}. Перезапуск через 10 секунд...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
