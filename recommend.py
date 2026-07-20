from config import MAX_SPEND_RUB_PER_CHECK

# Статичная база товаров (позже можно будет получать из парсера)
PRODUCTS = [
    {"name": "Молоко 1л", "price": 65},
    {"name": "Хлеб белый", "price": 30},
    {"name": "Масло сливочное 180г", "price": 120},
    {"name": "Яйца 10шт", "price": 85},
    {"name": "Сметана 200г", "price": 55},
    {"name": "Творог 200г", "price": 75},
    {"name": "Кефир 1л", "price": 60},
    {"name": "Батон нарезной", "price": 25},
    {"name": "Сахар 1кг", "price": 70},
    {"name": "Макароны 400г", "price": 45},
    {"name": "Рис 800г", "price": 90},
    {"name": "Гречка 800г", "price": 85},
    {"name": "Подсолнечное масло 1л", "price": 110},
    {"name": "Чай 50пак", "price": 80},
    {"name": "Печенье 200г", "price": 50},
]

def recommend_products(balance_balls):
    """
    balance_balls - количество баллов (апельсинок)
    Возвращает словарь с рекомендацией:
      - products: список товаров
      - total_price: общая стоимость корзины
      - spend_rub: сколько спишется баллами (в рублях)
      - spend_balls: сколько спишется баллами (в баллах)
      - user_pays: сколько нужно доплатить
      - max_possible: максимум, что можно списать за чек
      - remaining_balls: остаток баллов после списания
    """
    max_spend_rub = min(balance_balls // 10, MAX_SPEND_RUB_PER_CHECK)
    max_spend_balls = max_spend_rub * 10

    # Нужно набрать товаров на сумму в 2 раза больше (чтобы 50% покрыть баллами)
    target_total = max_spend_rub * 2

    # Жадный подбор (подбираем товары, пока не наберем нужную сумму)
    remaining = target_total
    chosen = []
    for product in sorted(PRODUCTS, key=lambda x: x["price"], reverse=True):
        if remaining <= 0:
            break
        if product["price"] <= remaining:
            chosen.append(product)
            remaining -= product["price"]

    # Если ничего не подобралось (вдруг все товары дороже) — берём самый дешёвый
    if not chosen:
        cheapest = min(PRODUCTS, key=lambda x: x["price"])
        chosen = [cheapest]

    total = sum(p["price"] for p in chosen)

    # Фактически спишется 50% от стоимости, но не больше лимита
    actual_spend_rub = min(total // 2, max_spend_rub)
    actual_spend_balls = actual_spend_rub * 10
    user_pays = total - actual_spend_rub

    return {
        "products": chosen,
        "total_price": total,
        "spend_rub": actual_spend_rub,
        "spend_balls": actual_spend_balls,
        "user_pays": user_pays,
        "max_possible": max_spend_rub,
        "remaining_balls": balance_balls - actual_spend_balls
    }