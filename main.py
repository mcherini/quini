import os
import requests
import io
from telegram import Bot
import asyncio
from PyPDF2 import PdfReader

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PDF_URL = "https://jasper2.loteriasantafe.gov.ar/Ejecutar_Reportes2.php?ruta_reporte=/Reports/CAS/Extractos_CAS/extrpp&formato=PDF&param_ID_sor=0314E762-02A3-4265-BE0E-BC51A25D5C1B"

async def send_message(text):
    bot = Bot(token=TOKEN)
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        await bot.send_message(chat_id=CHAT_ID, text=chunk)

def get_pdf_content():
    try:
        print("[INFO] Descargando PDF oficial...")
        response = requests.get(PDF_URL, timeout=15)
        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            return None

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        # Extraemos todo el texto del PDF
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        if not full_text.strip():
            print("[ERROR] No se pudo extraer texto del PDF.")
            return None

        print("[INFO] Texto extraído del PDF.")
        return full_text
    except Exception as e:
        print(f"[ERROR] Falló la descarga o lectura del PDF: {e}")
        return None

def main():
    text = get_pdf_content()
    if text:
        asyncio.run(send_message("📄 Resultados Quini 6 (Extracto Oficial):\n\n" + text))
    else:
        asyncio.run(send_message("⚠️ No se pudo obtener el PDF oficial."))

if __name__ == "__main__":
    main()
