import requests
from telegram import Bot
import os

# Configuración desde variables de entorno
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MY_NUMBERS = [4, 8, 10, 13, 17, 33]

# URL oficial resultados (Quini 6)
RESULT_URL = "https://www.quini-6-resultados.com.ar/api/ultimosorteo"

def get_results():
    response = requests.get(RESULT_URL)
    data = response.json()
    # Extraemos todas las modalidades: Tradicional, Segunda, Revancha
    trad = data['Tradicional']['numeros']
    segunda = data['Segunda']['numeros']
    revancha = data['Revancha']['numeros']
    return [trad, segunda, revancha]

def check_match(results):
    message = ""
    for idx, modality in enumerate(["Tradicional", "Segunda", "Revancha"]):
        aciertos = len(set(MY_NUMBERS) & set(results[idx]))
        if aciertos >= 4:
            message += f"🎉 ¡TENÉS {aciertos} aciertos en {modality}! {results[idx]}\n"
        else:
            message += f"{modality}: {aciertos} aciertos. Números: {results[idx]}\n"
    return message

def send_message(text):
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text)

def main():
    results = get_results()
    message = check_match(results)
    send_message(message)

if __name__ == "__main__":
    main()
