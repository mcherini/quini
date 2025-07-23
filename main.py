import os
import requests
from telegram import Bot
import asyncio
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.loteriasantafe.gov.ar/index.php?option=com_loteria&view=resultados&juego=quini6"

async def send_message(text):
    bot = Bot(token=TOKEN)
    # Si el texto es muy largo, dividimos en partes
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        await bot.send_message(chat_id=CHAT_ID, text=chunk)

def get_page_content():
    try:
        print("[INFO] Descargando página oficial...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        # Extraer texto visible
        text = soup.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        print(f"[ERROR] No se pudo obtener la página: {e}")
        return None

def main():
    text = get_page_content()
    if text:
        print("[INFO] Texto obtenido, enviando a Telegram...")
        asyncio.run(send_message(text))
    else:
        print("[ERROR] No se pudo obtener contenido.")

if __name__ == "__main__":
    main()
