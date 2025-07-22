import os
import requests
from telegram import Bot

# Variables de entorno
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Tu jugada
MY_NUMBERS = [4, 8, 10, 13, 17, 33]

# API resultados Quini 6
RESULT_URL = "https://www.quini-6-resultados.com.ar/api/ultimosorteo"

def get_results():
    response = requests.get(RESULT_URL)
    data = response.json()
    return {
        "Tradicional": [int(x) for x in data['Tradicional']['numeros']],
        "Segunda": [int(x) for x in data['Segunda']['numeros']],
        "Revancha": [int(x) for x in data['Revancha']['numeros']]
    }

def check_results(results):
    winners = []
    for modalidad, nums in results.items():
        aciertos = len(set(MY_NUMBERS) & set(nums))
        if aciertos >= 4:
            winners.append((modalidad, aciertos, nums))
    return winners

def send_message(winners):
    bot = Bot(token=TOKEN)
    if winners:
        message = "🎉 ¡ATENCIÓN! Tu jugada tuvo premio:\n\n"
        for modalidad, aciertos, nums in winners:
            message += f"✅ {modalidad}: {aciertos} aciertos\nNúmeros: {nums}\n\n"
        message += "🔗 Ver sorteo: https://www.loteriasantafe.gov.ar"
    else:
        message = "📢 Sorteo verificado: No hubo 4 o más aciertos esta vez."
    bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    results = get_results()
    winners = check_results(results)
    send_message(winners)

if __name__ == "__main__":
    main()
