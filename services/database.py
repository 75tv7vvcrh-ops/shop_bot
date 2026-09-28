import logging
import asyncpg
from config import PG_USER, PG_PASSWORD, PG_DATABASE, PG_HOST, PG_PORT

async def get_connection():
    return await asyncpg.connect(
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DATABASE,
        host=PG_HOST,
        port=PG_PORT
    )

async def init_db():
    logging.info("Инициализация базы данных PostgreSQL...")
    conn = await get_connection()
    try:
        # 1. Таблица пользователей
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                name TEXT,
                age INT,
                city TEXT,
                source TEXT DEFAULT 'direct',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Таблица товаров
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL,
                stock INT DEFAULT 10,
                category TEXT DEFAULT 'Общее',
                image_id TEXT
            );
        """)

        # Миграция: Добавляем отсутствующие колонки, если таблица уже существовала
        await conn.execute("""
            ALTER TABLE products ADD COLUMN IF NOT EXISTS description TEXT;
            ALTER TABLE products ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'Общее';
            ALTER TABLE products ADD COLUMN IF NOT EXISTS image_id TEXT;
            ALTER TABLE products ADD COLUMN IF NOT EXISTS stock INT DEFAULT 10;
        """)

        # 3. Таблица корзины
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                quantity INT DEFAULT 1
            );
        """)

        # 4. Таблица заказов (с правильной колонкой total_amount)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                total_amount NUMERIC(10, 2) NOT NULL,
                status TEXT DEFAULT 'NEW',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Наполняем стартовыми товарами, если таблица пуста
        count = await conn.fetchval("SELECT COUNT(*) FROM products")
        if count == 0:
            await conn.execute("""
                INSERT INTO products (name, description, price, stock, category) VALUES
                ('iPhone 15 Pro', 'Флагманский смартфон Apple', 99990.00, 5, 'Электроника'),
                ('MacBook Air M2', 'Мощный и легкий ноутбук', 124990.00, 3, 'Электроника'),
                ('AirPods Pro 2', 'Беспроводные наушники с шумоподавлением', 24990.00, 10, 'Аксессуары');
            """)
            logging.info("Тестовые товары добавлены в каталог.")

    finally:
        await conn.close()

async def add_user_if_not_exists(user_id: int, source: str = "direct"):
    conn = await get_connection()
    try:
        await conn.execute("""
            INSERT INTO users (user_id, source)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id, source)
    finally:
        await conn.close()

async def save_user_profile(user_id: int, name: str, age: int, city: str):
    conn = await get_connection()
    try:
        await conn.execute("""
            UPDATE users
            SET name = $1, age = $2, city = $3
            WHERE user_id = $4
        """, name, age, city, user_id)
    finally:
        await conn.close()