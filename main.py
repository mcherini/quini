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

# URL oficial de resultados
URL = "https://www.loteriasantafe.gov.ar/resultados/quini-6"

# ----------- OBTENER RESULTADOS (SCRAPING ROBUSTO) -------------
def get_results():
    try:
        print("[INFO] Obteniendo resultados desde Lotería Santa Fe...")
        page = requests.get(URL, timeout=10)
        if page.status_code != 200:
            print(f"[ERROR] HTTP {page.status_code}")
            return None

        soup = BeautifulSoup(page.content, "html.parser")

        # Buscar TODOS los números que están dentro de etiquetas <li>
        all_numbers = [int(n.text.strip()) for n in soup.find_all("li") if n.text.strip().isdigit()]

        if len(all_numbers) < 18:
            print(f"[ERROR] Solo encontré {len(all_numbers)} números. Estructura inesperada.")
            return None

        # Tomamos los primeros 18 números (3 jugadas de 6 números)
        tradicional = all_numbers[0:6]
        segunda = all_numbers[6:12]
        revancha = all_numbers[12:18]

        print("[INFO] Resultados extraídos:", tradicional, segunda, revancha)

        return {
            "Tradicional": tradicional,
            "Segunda": segunda,
            "Revancha": revancha
        }
    except Exception as e:
        print(f"[ERROR] Falló el scraping: {e}")
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
        message = "⚠️ No se pudieron obtener los resultados del Quini 6.\n" \
                  "🔗 Revisar manualmente: https://www.loteriasantafe.gov.ar/resultados/quini-6"
    else:
        message = "📢 Resultados Quini 6:\n\n"
        for modalidad, aciertos, nums in winners:
            if aciertos >= 4:
                message += f"🎉 {modalidad}: {aciertos} aciertos ✅\nNúmeros: {nums}\n\n"
            else:
                message += f"{modalidad}: {aciertos} aciertos\nNúmeros: {nums}\n\n"
        message += "🔗 Ver sorteo: https://www.loteriasantafe.gov.ar/resultados/quini-6"

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

