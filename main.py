import os
import requests
import io
from telegram import Bot
import asyncio
from PyPDF2 import PdfReader
import re

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Tu jugada personalizada
MY_NUMBERS = [4, 8, 10, 13, 17, 33]

PDF_URL = "https://jasper2.loteriasantafe.gov.ar/Ejecutar_Reportes2.php?ruta_reporte=/Reports/CAS/Extractos_CAS/extrpp&formato=PDF&param_ID_sor=0314E762-02A3-4265-BE0E-BC51A25D5C1B"

async def send_message(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

def get_pdf_content():
    try:
        response = requests.get(PDF_URL, timeout=15)
        if response.status_code != 200:
            return None

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return None

def extract_numbers(text, title):
    """Encuentra el título y toma los 6 números siguientes (1 a 45)."""
    idx = text.find(title)
    if idx == -1:
        return []
    fragment = text[idx: idx + 200]  # Toma un bloque grande después del título
    numbers = re.findall(r"\b\d{1,2}\b", fragment)
    numbers = [n for n in numbers if 1 <= int(n) <= 45]
    return numbers[:6]

def parse_results(text):
    try:
        concurso = re.search(r"CONCURSO Nº (\d+)", text)
        fecha = re.search(r"(\d{2} DE [A-ZÁÉÍÓÚa-záéíóú]+ DE \d{4})", text)

        # Extraer números correctos
        tradicional = extract_numbers(text, "TRADICIONAL PRIMER SORTEO")
        segunda = extract_numbers(text, "TRADICIONAL LA SEGUNDA DEL QUINI")
        revancha = extract_numbers(text, "REVANCHA")
        siempre_sale = extract_numbers(text, "SIEMPRE SALE")

        pozo_extra = re.search(r"PREMIO EXTRA\s*\$([\d\.\,]+)", text)
        prox_pozo = re.search(r"POZO ESTIMADO\s*\$([\d\.\,]+)", text)

        # Calcular aciertos
        def aciertos(jugada):
            return len(set(map(int, jugada)) & set(MY_NUMBERS))

        msg = f"""
📢 QUINI 6 - CONCURSO {concurso.group(1) if concurso else 'N/D'}
📆 {fecha.group(1) if fecha else 'Fecha no encontrada'}

🎯 Tradicional: {' – '.join(tradicional)} ✅ Aciertos: {aciertos(tradicional)}
🎯 La Segunda: {' – '.join(segunda)} ✅ Aciertos: {aciertos(segunda)}
🎯 Revancha: {' – '.join(revancha)} ✅ Aciertos: {aciertos(revancha)}
🎯 Siempre Sale: {' – '.join(siempre_sale)} ✅ Aciertos: {aciertos(siempre_sale)}

💰 Pozo Extra: ${pozo_extra.group(1) if pozo_extra else 'N/D'}
💰 Próximo Pozo Estimado: ${prox_pozo.group(1) if prox_pozo else 'N/D'}

🎟️ Tu jugada: {', '.join(map(str, MY_NUMBERS))}

🔗 Ver PDF oficial: {PDF_URL}
"""
        return msg.strip()
    except Exception as e:
        return f"[ERROR] Falló el formateo: {e}"

def main():
    text = get_pdf_content()
    if text:
        parsed = parse_results(text)
        asyncio.run(send_message(parsed))
    else:
        asyncio.run(send_message("⚠️ No se pudo obtener el PDF oficial."))

if __name__ == "__main__":
    main()
