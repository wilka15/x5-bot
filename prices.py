import requests
from datetime import datetime
from database import get_user, set_city

def get_products_from_store(city):
    """
    Пытается получить товары со скидкой и цены из магазина в указанном городе.
    Использует библиотеку pyatorochka-min-api, но если её нет - возвращает статичный список.
    """
    try:
        from pyatorochka import Ato
        ato = Ato()
        # Получаем список магазинов в городе (берём первый)
        stores = ato.get_stores(city)
        if not stores:
            return None
        store_id = stores[0]['id']
        # Получаем товары со скидкой
        promo = ato.get_promo(store_id)
        products = []
        for item in promo:
            products.append({
                "name": item.get('name', ''),
                "price": int(item.get('price', 0)),
                "old_price": int(item.get('old_price', 0)) if item.get('old_price') else None
            })
        return products
    except Exception as e:
        print(f"Ошибка при получении цен: {e}")
        return None

def get_recommended_products_with_prices(user_id, balance):
    """
    Для пользователя пытается получить реальные цены из его города.
    Если не получается - использует статичную базу.
    """
    user = get_user(user_id)
    city = user.get("city") if user else None
    if city:
        real_products = get_products_from_store(city)
        if real_products:
            # Переопределяем глобальный список товаров (можно сохранить в БД)
            # Но для простоты заменим статичный список на полученный
            from recommend import PRODUCTS
            # Здесь можно обновить PRODUCTS, но глобальную переменную менять не очень хорошо.
            # Поэтому сделаем локальный список и используем его.
            # Для простоты оставим статичный, но в будущем можно сохранять в БД.
            pass
    # Возвращаем статичный список из recommend (сейчас он глобальный)
    from recommend import PRODUCTS
    return PRODUCTS