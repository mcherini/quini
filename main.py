import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio

# Variables de entorno (Railway)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Tu jugada fija
MY_NUMBERS = [4, 8, 10, 13, 17, 33]

# URL de búsqueda en Google
GOOGLE_SEARCH_URL = "https://www.google.com/search?q=quini+6"

# ----------- OBTENER RESULTADOS DESDE GOOGLE -------------
def get_results():
    try:
        print("[INFO] Buscando resultados en Google...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        page = requests.get(GOOGLE_SEARCH_URL, headers=headers, timeout=10)
        if page.status_code != 200:
            print(f"[ERROR] HTTP {page.status_code}")
            return None

        soup = BeautifulSoup(page.text, "html.parser")

        # Buscar todos los spans que contienen números
        spans = soup.select("span")
        numbers = [int(s.text) for s in spans if s.text.isdigit()]

        print(f"[DEBUG] Números detectados en Google: {numbers}")

        if len(numbers) < 18:
            print(f"[ERROR] No se encontraron suficientes números (encontrados: {len(numbers)}).")
            return None

        # Tomamos los primeros 18 números (3 jugadas de 6)
        tradicional = numbers[0:6]
        segunda = numbers[6:12]
        revancha = numbers[12:18]

        print("[INFO] Resultados extraídos desde Google:", tradicional, segunda, revancha)
        return {
            "Tradicional": tradicional,
            "Segunda": segunda,
            "Revancha": revancha
        }
    except Exception as e:
        print(f"[ERROR] Falló la extracción desde Google: {e}")
        return None

# ----------- CHEQUEAR RESULTADOS -------------
def check_results(results):
    winners = []
    for modalidad, nums in results.items():
        aciertos = len(set(MY_NUMBERS) & set(nums))
        winners.append((modalidad, aciertos, nums))
    return winners

# ----------- ENVIAR MENSAJE TELEGRAM -------------
async def send_message(winners, error=False):
    bot = Bot(token=TOKEN)
    if error:
        message = "⚠️ No se pudieron obtener los resultados del Quini 6 desde Google.\n" \
                  "🔗 Revisar manualmente: https://www.google.com/search?q=quini+6"
    else:
        message = "📢 Resultados Quini 6:\n\n"
        for modalidad, aciertos, nums in winners:
            if aciertos >= 4:
                message += f"🎉 {modalidad}: {aciertos} aciertos ✅\nNúmeros: {nums}\n\n"
            else:
                message += f"{modalidad}: {aciertos} aciertos\nNúmeros: {nums}\n\n"
        message += "🔗 Ver sorteo: https://www.google.com/search?q=quini+6"

    await bot.send_message(chat_id=CHAT_ID, text=message)

# ----------- MAIN -------------
def main():
    results = get_results()
    if results:
        winners = check_results(results)
        asyncio.run(send_message(winners))
    else:
        asyncio.run(send_message([], error=True))

if __name__ == "__main__":
    main()

