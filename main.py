import asyncio
import requests
from aiogram import Bot
from dotenv import load_dotenv
import os

# Завантажуємо змінні з .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")        # Токен твого Telegram-бота
CHAT_ID = os.getenv("CHAT_ID")        # ID користувача/каналу
API_TOKEN = os.getenv("API_TOKEN")    # Токен від alerts.in.ua
TARGET_DISTRICT = "Прилуцький район"  # Район для моніторингу

bot = Bot(token=TOKEN)
previous_alert = None

async def check_alerts():
    global previous_alert
    url = f"https://api.alerts.in.ua/v1/alerts/active.json?token={API_TOKEN}"

    while True:
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            # Фільтруємо по Чернігівській області та Прилуцькому району
            pryluky = next(
                (a for a in data if 
                 a.get("region") == "Чернігівська область" and 
                 a.get("district") == TARGET_DISTRICT),
                None
            )

            if not pryluky:
                print(f"[WARN] {TARGET_DISTRICT} не знайдено у відповіді API")
                await asyncio.sleep(30)
                continue

            alert = pryluky.get("alert", False)

            # Перевірка зміни стану
            if alert != previous_alert:
                previous_alert = alert
                if alert:
                    text = f"🚨 Повітряна тривога у {TARGET_DISTRICT}!"
                else:
                    text = f"✅ Відбій у {TARGET_DISTRICT}!"
                await bot.send_message(CHAT_ID, text)
                print(f"[INFO] {text}")

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(30)  # перевірка кожні 30 секунд

async def main():
    await check_alerts()

if __name__ == "__main__":
    asyncio.run(main())
