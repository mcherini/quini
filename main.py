import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Variables de entorno (Railway)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Tu jugada fija
MY_NUMBERS = [4, 8, 10, 13, 17, 33]

# URL oficial del Quini 6 (Lotería de Santa Fe)
URL = "https://www.loteriasantafe.gov.ar/juego/quini6"

# Cambiar a True para probar con datos simulados
TEST_MODE = True

# ----------- OBTENER RESULTADOS -------------
def get_results():
    if TEST_MODE:
        # Simulación: forzamos premio para probar alertas
        return {
            "Tradicional": [4, 8, 10, 13, 17, 33],  # ¡6 aciertos!
            "Segunda": [5, 12, 19, 25, 33, 44],
            "Revancha": [3, 6, 8, 22, 27, 35]
        }
    else:
        try:
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")

            # Busca todos los bloques donde aparecen las bolillas
            juegos = soup.find_all("div", class_="numeros")
            if not juegos or len(juegos) < 3:
                return None

            # Extraer números de cada modalidad
            tradicional = [int(n.text) for n in juegos[0].find_all("span")]
            segunda = [int(n.text) for n in juegos[1].find_all("span")]
            revancha = [int(n.text) for n in juegos[2].find_all("span")]

            return {
                "Tradicional": tradicional,
                "Segunda": segunda,
                "Revancha": revancha
            }
        except Exception as e:
            print("Error scraping:", e)
            return None

# ----------- CHEQUEAR RESULTADOS -------------
def check_results(results):
    winners = []
    for modalidad, nums in results.items():
        aciertos = len(set(MY_NUMBERS) & set(nums))
        if aciertos >= 4:  # Solo avisamos si hay premio
            winners.append((modalidad, aciertos, nums))
    return winners

# ----------- ENVIAR MENSAJE TELEGRAM -------------
async def send_message(winners):
    bot = Bot(token=TOKEN)
    if winners:
        message = "🎉 ¡ATENCIÓN! Tu jugada tuvo premio:\n\n"
        for modalidad, aciertos, nums in winners:
            message += f"✅ {modalidad}: {aciertos} aciertos\nNúmeros: {nums}\n\n"
        message += "🔗 Ver sorteo: https://www.loteriasantafe.gov.ar/juego/quini6"
    else:
        message = "📢 Sorteo verificado: No hubo 4 o más aciertos esta vez."
    await bot.send_message(chat_id=CHAT_ID, text=message)

# ----------- MAIN -------------
def main():
    import asyncio
    results = get_results()
    if results:
        winners = check_results(results)
        asyncio.run(send_message(winners))
    else:
        asyncio.run(send_message([]))

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
