import os
from telegram import Bot
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def send_test_message():
    bot = Bot(token=TOKEN)
    message = """
📢 Quini 6 - Resultados Simulados
📆 Sorteo: 20 de Julio de 2025

🎯 Tradicional:
04 – 07 – 17 – 25 – 27 – 36

🎯 Segunda Vuelta:
00 – 04 – 06 – 09 – 20 – 37

🎯 Revancha:
19 – 22 – 25 – 31 – 35 – 38

🎯 Siempre Sale:
10 – 14 – 26 – 34 – 38 – 45

🔗 Más info: https://www.google.com/search?q=quini+6
"""
    await bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    asyncio.run(send_test_message())

if __name__ == "__main__":
    main()
