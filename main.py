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

# URL oficial del Quini 6
URL = "https://www.loteriasantafe.gov.ar/juego/quini6"

# ----------- OBTENER RESULTADOS (SCRAPING REAL) -------------
def get_results():
    try:
        page = requests.get(URL, timeout=10)
        if page.status_code != 200:
            print(f"Error: HTTP {page.status_code}")
            return None

        soup = BeautifulSoup(page.content, "html.parser")
        juegos = soup.find_all("div", class_="numeros")

        if not juegos or len(juegos) < 3:
            print("Error: No se encontraron resultados en la página.")
            return None

        tradicional = [int(n.text) for n in juegos[0].find_all("span")]
        segunda = [int(n.text) for n in juegos[1].find_all("span")]
        revancha = [int(n.text) for n in juegos[2].find_all("span")]

        return {
            "Tradicional": tradicional,
            "Segunda": segunda,
            "Revancha": revancha
        }
    except Exception as e:
        print(f"Error en scraping: {e}")
        return None

# ----------- CHEQUEAR RESULTADOS -------------
def check_results(results):
    winners = []
    for modalidad, nums in results.items():
        aciertos = len(set(MY_NUMBERS) & set(nums))
        winners.append((modalidad, aciertos, nums))
    return winners

# ----------- ENVIAR MENSAJE TELEGRAM -------------
async def send_message(winners):
    bot = Bot(token=TOKEN)

    # Armamos el mensaje con TODOS los resultados
    message = "📢 Resultados Quini 6:\n\n"
    for modalidad, aciertos, nums in winners:
        if aciertos >= 4:
            message += f"🎉 {modalidad}: {aciertos} aciertos ✅\nNúmeros: {nums}\n\n"
        else:
            message += f"{modalidad}: {aciertos} aciertos\nNúmeros: {nums}\n\n"

    message += "🔗 Ver sorteo: https://www.loteriasantafe.gov.ar/juego/quini6"

    await bot.send_message(chat_id=CHAT_ID, text=message)

# ----------- MAIN -------------
def main():
    results = get_results()
    if results:
        winners = check_results(results)
        asyncio.run(send_message(winners))
    else:
        print("No se pudieron obtener resultados.")

if __name__ == "__main__":
    main()

