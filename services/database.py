import logging
import asyncpg

from config import (
    PG_USER,
    PG_PASSWORD,
    PG_DATABASE,
    PG_HOST,
    PG_PORT
)


pool = None


async def init_db():
    global pool

    logging.info("Инициализация базы данных PostgreSQL...")

    pool = await asyncpg.create_pool(
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DATABASE,
        host=PG_HOST,
        port=PG_PORT,
        min_size=1,
        max_size=10
    )

    async with pool.acquire() as conn:

        # 1. Пользователи
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

        # 2. Товары
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

        await conn.execute("""
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS description TEXT;

            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'Общее';

            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS image_id TEXT;

            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS stock INT DEFAULT 10;
        """)

        # 3. Корзина
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                product_id INT NOT NULL
                    REFERENCES products(id)
                    ON DELETE CASCADE,
                quantity INT DEFAULT 1
            );
        """)

        # 4. Заказы
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                total_amount NUMERIC(10, 2) NOT NULL,
                status TEXT DEFAULT 'NEW',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 5. Состав заказов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INT NOT NULL
                    REFERENCES orders(id)
                    ON DELETE CASCADE,
                product_id INT NOT NULL
                    REFERENCES products(id)
                    ON DELETE CASCADE,
                product_name TEXT,
                price NUMERIC(10, 2),
                quantity INT NOT NULL
            );
        """)

        await conn.execute("""
            ALTER TABLE order_items
            ADD COLUMN IF NOT EXISTS product_name TEXT;

            ALTER TABLE order_items
            ADD COLUMN IF NOT EXISTS price NUMERIC(10, 2);

            ALTER TABLE order_items
            ADD COLUMN IF NOT EXISTS quantity INT DEFAULT 1;
        """)

        await conn.execute("""
            UPDATE order_items oi
            SET product_name = p.name
            FROM products p
            WHERE oi.product_id = p.id
              AND oi.product_name IS NULL;
        """)

        await conn.execute("""
            UPDATE order_items oi
            SET price = p.price
            FROM products p
            WHERE oi.product_id = p.id
              AND oi.price IS NULL;
        """)

        # 6. Заблокированные пользователи
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id BIGINT PRIMARY KEY,
                reason TEXT DEFAULT 'Нарушение правил',
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        await conn.execute("""
            ALTER TABLE banned_users
            ADD COLUMN IF NOT EXISTS banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """)

        # 7. Стартовые товары
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM products"
        )

        if count == 0:
            await conn.execute("""
                INSERT INTO products
                (name, description, price, stock, category)
                VALUES
                (
                    'iPhone 15 Pro',
                    'Флагманский смартфон Apple',
                    99990.00,
                    5,
                    'Электроника'
                ),
                (
                    'MacBook Air M2',
                    'Мощный и легкий ноутбук',
                    124990.00,
                    3,
                    'Электроника'
                ),
                (
                    'AirPods Pro 2',
                    'Беспроводные наушники с шумоподавлением',
                    24990.00,
                    10,
                    'Аксессуары'
                );
            """)

            logging.info(
                "Тестовые товары добавлены в каталог."
            )


async def get_connection():
    if pool is None:
        raise RuntimeError(
            "Пул PostgreSQL не инициализирован. "
            "Сначала вызови init_db()."
        )

    return await pool.acquire()


async def close_pool():
    global pool

    if pool is not None:
        await pool.close()
        pool = None


async def add_user_if_not_exists(
    user_id: int,
    source: str = "direct"
):
    conn = await get_connection()

    try:
        await conn.execute("""
            INSERT INTO users (user_id, source)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id, source)

    finally:
        await pool.release(conn)


async def save_user_profile(
    user_id: int,
    name: str,
    age: int,
    city: str
):
    conn = await get_connection()

    try:
        await conn.execute("""
            UPDATE users
            SET name = $1,
                age = $2,
                city = $3
            WHERE user_id = $4
        """, name, age, city, user_id)

    finally:
        await pool.release(conn)


async def ban_user(
    user_id: int,
    reason: str = "Нарушение правил"
):
    conn = await get_connection()

    try:
        await conn.execute(
            """
            INSERT INTO banned_users (user_id, reason)
            VALUES ($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET
                reason = EXCLUDED.reason,
                banned_at = CURRENT_TIMESTAMP
            """,
            user_id,
            reason
        )

    finally:
        await pool.release(conn)


async def unban_user(user_id: int):
    conn = await get_connection()

    try:
        await conn.execute(
            "DELETE FROM banned_users WHERE user_id = $1",
            user_id
        )

    finally:
        await pool.release(conn)


async def is_user_banned(user_id: int):
    conn = await get_connection()

    try:
        return await conn.fetchrow(
            """
            SELECT user_id, reason
            FROM banned_users
            WHERE user_id = $1
            """,
            user_id
        )

    finally:
        await pool.release(conn)