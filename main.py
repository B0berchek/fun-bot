import random
import json
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
DATA_FILE = BASE_DIR / "trees.json"


# конфиг
DEFAULT_CONFIG = {
    "token": ""
}

def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(DEFAULT_CONFIG, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Создан файл {CONFIG_FILE}")
        print("Впиши в него токен бота и запусти программу снова.")
        sys.exit()

    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

    if not config.get("token"):
        print(f"В файле {CONFIG_FILE} не указан токен.")
        print("Впиши его в поле \"token\" и запусти программу снова.")
        sys.exit()

    return config

config = load_config()


# сама работа команд
data = {}
if DATA_FILE.exists():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))


async def grow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    change = random.randint(-5, 15)
    data[uid] = data.get(uid, 0) + change

    DATA_FILE.write_text(json.dumps(data), encoding="utf-8")

    if change >= 0:
        text = f"{user.first_name}, ваше дерево выросло на {change} см"
    else:
        text = f"{user.first_name}, ваше дерево уменьшилось на {abs(change)} см"

    text += f"\nТеперь его высота: {data[uid]} см"
    await update.message.reply_text(text)


# создание бота
builder = (
    ApplicationBuilder()
    .token(config["token"])
    .proxy("socks5://123.45.67.89:1080")
    .get_updates_proxy("socks5://123.45.67.89:1080")
    .connect_timeout(30)
    .read_timeout(30)
)

app = builder.build()
app.add_handler(CommandHandler("grow", grow))
app.run_polling()