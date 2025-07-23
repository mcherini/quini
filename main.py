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
        if response.status_code == 200:
            return response.content
    except:
        return None
    return None

def extract_text_from_pdf(pdf_data):
    images = convert_from_bytes(pdf_data, dpi=200)
    full_text = ""
    for img in images:
        full_text += pytesseract.image_to_string(img, lang="spa") + "\n"
    return full_text

def extract_section_numbers(text, section_name):
    # Buscar la sección y tomar texto cercano (300 caracteres)
    pattern = rf"{section_name}.*?((?:\d+\s*){{6,10}})"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        nums = re.findall(r"\b\d{1,2}\b", match.group(1))
        nums = [int(n) for n in nums if 1 <= int(n) <= 45]
        return nums[:6]
    return []

def parse_results(text):
    tradicional = extract_section_numbers(text, "TRADICIONAL PRIMER SORTEO")
    segunda = extract_section_numbers(text, "TRADICIONAL LA SEGUNDA DEL QUINI")
    revancha = extract_section_numbers(text, "REVANCHA")
    siempre_sale = extract_section_numbers(text, "SIEMPRE SALE")

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
    return message

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
