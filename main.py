import os
import requests
import io
from telegram import Bot
import asyncio
from pdf2image import convert_from_bytes
import pytesseract
import re

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MY_NUMBERS = [4, 8, 10, 13, 17, 33]

PDF_URL = "https://jasper2.loteriasantafe.gov.ar/Ejecutar_Reportes2.php?ruta_reporte=/Reports/CAS/Extractos_CAS/extrpp&formato=PDF&param_ID_sor=0314E762-02A3-4265-BE0E-BC51A25D5C1B"

async def send_message(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

def download_pdf():
    try:
        response = requests.get(PDF_URL, timeout=15)
        if response.status_code != 200:
            return None
        return response.content
    except:
        return None

def extract_text_from_pdf(pdf_data):
    # Convertimos el PDF en imágenes
    images = convert_from_bytes(pdf_data, dpi=200)
    full_text = ""
    for img in images:
        # OCR con pytesseract
        text = pytesseract.image_to_string(img, lang="spa")
        full_text += text + "\n"
    return full_text

def parse_results(text):
    try:
        # Buscar números (1-2 dígitos) y filtrarlos (1-45)
        all_numbers = re.findall(r"\b\d{1,2}\b", text)
        all_numbers = [int(n) for n in all_numbers if 1 <= int(n) <= 45]

        # Tomamos los primeros 24 números válidos
        tradicional = all_numbers[0:6]
        segunda = all_numbers[6:12]
        revancha = all_numbers[12:18]
        siempre_sale = all_numbers[18:24]

        # Calcular aciertos
        def aciertos(jugada):
            return len(set(jugada) & set(MY_NUMBERS))

        message = f"""
📢 QUINI 6 - RESULTADOS OCR
🎯 Tradicional: {' – '.join(map(str, tradicional))} ✅ Aciertos: {aciertos(tradicional)}
🎯 La Segunda: {' – '.join(map(str, segunda))} ✅ Aciertos: {aciertos(segunda)}
🎯 Revancha: {' – '.join(map(str, revancha))} ✅ Aciertos: {aciertos(revancha)}
🎯 Siempre Sale: {' – '.join(map(str, siempre_sale))} ✅ Aciertos: {aciertos(siempre_sale)}

🎟️ Tu jugada: {', '.join(map(str, MY_NUMBERS))}

🔗 PDF Oficial: {PDF_URL}
"""
        return message.strip()
    except Exception as e:
        return f"[ERROR] Falló el OCR: {e}"

def main():
    pdf_data = download_pdf()
    if pdf_data:
        text = extract_text_from_pdf(pdf_data)
        parsed = parse_results(text)
        asyncio.run(send_message(parsed))
    else:
        asyncio.run(send_message("⚠️ No se pudo descargar el PDF oficial."))

if __name__ == "__main__":
    main()

