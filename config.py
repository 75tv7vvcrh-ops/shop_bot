import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / "codes.env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"❌ Переменная окружения {name} не найдена.\n"
            f"Проверь файл: {ENV_PATH}"
        )

    return value


# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        f"❌ BOT_TOKEN не найден в {ENV_PATH}.\n"
        f"Добавь строку:\n"
        f"BOT_TOKEN=твой_токен"
    )


ADMIN_ID = int(
    get_required_env("ADMIN_ID")
)


# PostgreSQL
PG_USER = get_required_env("PG_USER")
PG_PASSWORD = get_required_env("PG_PASSWORD")
PG_DATABASE = get_required_env("PG_DATABASE")
PG_HOST = get_required_env("PG_HOST")

PG_PORT = int(
    os.getenv("PG_PORT", "5432")
)