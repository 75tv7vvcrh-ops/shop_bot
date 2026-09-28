import os
from pathlib import Path
from dotenv import load_dotenv

# Находим путь именно к файлу codes.env
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "codes.env"

# Принудительно загружаем переменные из codes.env
load_dotenv(dotenv_path=ENV_PATH, override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        f"❌ Ошибка: BOT_TOKEN не найден в {ENV_PATH}! "
        f"Убедись, что внутри есть строка: BOT_TOKEN=твой_токен"
    )

ADMIN_ID = int(os.getenv("ADMIN_ID", "8433028606"))

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_DATABASE = os.getenv("PG_DATABASE", "shop_db")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))