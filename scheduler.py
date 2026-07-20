from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from database import get_all_users

# Глобальные переменные
bot = None
scheduler = None

async def check_expiry():
    """Проверяет, у кого баллы сгорают через 3 дня, и шлёт напоминание"""
    if bot is None:
        return
    users = get_all_users()
    for user_id, balance, expire_date, notify_enabled in users:
        if not notify_enabled or expire_date is None:
            continue
        expire_dt = datetime.fromisoformat(expire_date)
        days_left = (expire_dt - datetime.now()).days
        if days_left == 3:
            rubles = balance // 10
            msg = (
                f"🍊 ВНИМАНИЕ! Через 3 дня сгорят {balance} баллов ({rubles} руб.)!\n"
                f"Успейте потратить их в Пятёрочке.\n"
                f"Чтобы получить подборку товаров, отправьте /recommend"
            )
            try:
                await bot.send_message(user_id, msg)
            except Exception as e:
                print(f"Не удалось отправить сообщение {user_id}: {e}")

def init_scheduler(bot_instance):
    """Инициализирует и запускает планировщик"""
    global bot, scheduler
    bot = bot_instance
    scheduler = AsyncIOScheduler()
    # Ежедневная проверка в 10:00
    scheduler.add_job(check_expiry, CronTrigger(hour=10, minute=0))
    scheduler.start()
    return scheduler