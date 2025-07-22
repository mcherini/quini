import os
import requests
from telegram import Bot
import asyncio

# Variables de entorno (Railway)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Tu jugada fija
MY_NUMBERS = [4, 8, 10, 13, 17, 33]

# API confiable para resultados del Quini 6
API_URL = "https://quinielas.ar/api/quini6"

# ----------- OBTENER RESULTADOS DESDE API -------------
def get_results():
    try:
        print("[INFO] Obteniendo resultados desde API...")
        response = requests.get(API_URL, timeout=10)
        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            return None

        data = response.json()
        if not data:
            print("[ERROR] No hay datos en la respuesta del API.")
            return None

        tradicional = data.get("tradicional", [])
        segunda = data.get("segunda", [])
        revancha = data.get("revancha", [])

        if len(tradicional) < 6 or len(segunda) < 6 or len(revancha) < 6:
            print("[ERROR] Resultados incompletos en API.")
            return None

        print("[INFO] Resultados obtenidos correctamente.")
        return {
            "Tradicional": tradicional,
            "Segunda": segunda,
            "Revancha": revancha
        }
    except Exception as e:
        print(f"[ERROR] Falló la obtención desde API: {e}")
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
                  "🔗 Revisar manualmente: https://quinielas.ar/quini6"
    else:
        message = "📢 Resultados Quini 6:\n\n"
        for modalidad, aciertos, nums in winners:
            if aciertos >= 4:
                message += f"🎉 {modalidad}: {aciertos} aciertos ✅\nNúmeros: {nums}\n\n"
            else:
                message += f"{modalidad}: {aciertos} aciertos\nNúmeros: {nums}\n\n"
        message += "🔗 Más info: https://quinielas.ar/quini6"

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

