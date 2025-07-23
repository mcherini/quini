import os
import requests
import io
from telegram import Bot
import asyncio
from PyPDF2 import PdfReader
import re

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PDF_URL = "https://jasper2.loteriasantafe.gov.ar/Ejecutar_Reportes2.php?ruta_reporte=/Reports/CAS/Extractos_CAS/extrpp&formato=PDF&param_ID_sor=0314E762-02A3-4265-BE0E-BC51A25D5C1B"

async def send_message(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

def get_pdf_content():
    try:
        print("[INFO] Descargando PDF oficial...")
        response = requests.get(PDF_URL, timeout=15)
        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            return None

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        # Extraer texto completo
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        return full_text
    except Exception as e:
        print(f"[ERROR] Falló la descarga o lectura del PDF: {e}")
        return None

def parse_results(text):
    try:
        # Concurso y fecha
        concurso = re.search(r"CONCURSO Nº (\d+)", text)
        fecha = re.search(r"(\d{2} DE [A-ZÁÉÍÓÚa-záéíóú]+ DE \d{4})", text)

        # Buscar secuencias de números (2 dígitos) en el texto
        numeros = re.findall(r"\b\d{1,2}\b", text)

        # Tradicional, Segunda, Revancha, Siempre Sale
        tradicional = " – ".join(numeros[0:6])
        segunda = " – ".join(numeros[6:12])
        revancha = " – ".join(numeros[12:18])
        siempre_sale = " – ".join(numeros[18:24])

        # Pozo Extra y próximo pozo
        pozo_extra = re.search(r"PREMIO EXTRA\s*\$([\d\.\,]+)", text)
        prox_pozo = re.search(r"PRÓXIMO POZO ESTIMADO\s*\$([\d\.\,]+)", text)

        message = f"""
📢 QUINI 6 - CONCURSO {concurso.group(1) if concurso else 'N/D'}
📆 {fecha.group(1) if fecha else 'Fecha no encontrada'}

🎯 Tradicional: {tradicional}
🎯 La Segunda: {segunda}
🎯 Revancha: {revancha}
🎯 Siempre Sale: {siempre_sale}

💰 Pozo Extra: ${pozo_extra.group(1) if pozo_extra else 'N/D'}
💰 Próximo Pozo Estimado: ${prox_pozo.group(1) if prox_pozo else 'N/D'}

🔗 Ver PDF oficial: {PDF_URL}
"""
        return message
    except Exception as e:
        print(f"[ERROR] Falló el formateo: {e}")
        return text[:1000]

def main():
    text = get_pdf_content()
    if text:
        parsed = parse_results(text)
        asyncio.run(send_message(parsed))
    else:
        asyncio.run(send_message("⚠️ No se pudo obtener el PDF oficial."))

if __name__ == "__main__":
    main()

