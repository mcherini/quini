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

# URL oficial del PDF (puede cambiar en cada sorteo)
PDF_URL = "https://jasper2.loteriasantafe.gov.ar/Ejecutar_Reportes2.php?ruta_reporte=/Reports/CAS/Extractos_CAS/extrpp&formato=PDF&param_ID_sor=0314E762-02A3-4265-BE0E-BC51A25D5C1B"

async def send_message(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

def get_pdf_content():
    try:
        print("[INFO] Descargando PDF oficial...")
        response = requests.get(PDF_URL, timeout=15)
        if response.status_code != 200:
            return None

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        return full_text
    except:
        return None

def extract_numbers_after(text, title):
    """Busca un título y extrae los 6 números que siguen."""
    pattern = rf"{title}\s*((?:\d{{1,2}}\s+){{6}})"
    match = re.search(pattern, text)
    if match:
        return [n for n in match.group(1).split() if n.isdigit()]
    return []

def parse_results(text):
    try:
        # Concurso y fecha
        concurso = re.search(r"CONCURSO Nº (\d+)", text)
        fecha = re.search(r"(\d{2} DE [A-ZÁÉÍÓÚa-záéíóú]+ DE \d{4})", text)

        # Extraer números correctos usando títulos
        tradicional = extract_numbers_after(text, "TRADICIONAL PRIMER SORTEO")
        segunda = extract_numbers_after(text, "TRADICIONAL LA SEGUNDA DEL QUINI")
        revancha = extract_numbers_after(text, "REVANCHA")
        siempre_sale = extract_numbers_after(text, "SIEMPRE SALE")

        # Pozo Extra y próximo pozo
        pozo_extra = re.search(r"PREMIO EXTRA\s*\$([\d\.\,]+)", text)
        prox_pozo = re.search(r"POZO ESTIMADO\s*\$([\d\.\,]+)", text)

        # Calcular aciertos
        def contar_aciertos(jugada):
            return len(set(map(int, jugada)) & set(MY_NUMBERS))

        aciertos_trad = contar_aciertos(tradicional)
        aciertos_seg = contar_aciertos(segunda)
        aciertos_rev = contar_aciertos(revancha)
        aciertos_ss = contar_aciertos(siempre_sale)

        message = f"""
📢 QUINI 6 - CONCURSO {concurso.group(1) if concurso else 'N/D'}
📆 {fecha.group(1) if fecha else 'Fecha no encontrada'}

🎯 Tradicional: {' – '.join(tradicional)} ✅ Aciertos: {aciertos_trad}
🎯 La Segunda: {' – '.join(segunda)} ✅ Aciertos: {aciertos_seg}
🎯 Revancha: {' – '.join(revancha)} ✅ Aciertos: {aciertos_rev}
🎯 Siempre Sale: {' – '.join(siempre_sale)} ✅ Aciertos: {aciertos_ss}

💰 Pozo Extra: ${pozo_extra.group(1) if pozo_extra else 'N/D'}
💰 Próximo Pozo Estimado: ${prox_pozo.group(1) if prox_pozo else 'N/D'}

🎟️ Tu jugada: {', '.join(map(str, MY_NUMBERS))}

🔗 Ver PDF oficial: {PDF_URL}
"""
        return message.strip()
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
