import os
import requests
import io
from telegram import Bot
import asyncio
from pdf2image import convert_from_bytes
import pytesseract
import re

# Variables de entorno
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Tu jugada personalizada
MY_NUMBERS = [4, 8, 10, 13, 17, 33]

# URL del PDF oficial
PDF_URL = "https://jasper2.loteriasantafe.gov.ar/Ejecutar_Reportes2.php?ruta_reporte=/Reports/CAS/Extractos_CAS/extrpp&formato=PDF&param_ID_sor=0314E762-02A3-4265-BE0E-BC51A25D5C1B"

async def send_message(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

def download_pdf():
    try:
        response = requests.get(PDF_URL, timeout=20)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"[ERROR] No se pudo descargar el PDF: {e}")
    return None

def extract_text_from_pdf(pdf_data):
    images = convert_from_bytes(pdf_data, dpi=200)
    full_text = ""
    for img in images:
        full_text += pytesseract.image_to_string(img, lang="spa") + "\n"
    return full_text

def extract_section_numbers(text, section_name):
    """Busca la sección y toma 6 números (0–45), permitiendo 00, eliminando duplicados y completando si faltan."""
    pattern = rf"{section_name}(.{{0,800}})"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        nums = re.findall(r"\b\d{1,2}\b", match.group(1))
        nums = [int(n) for n in nums if 0 <= int(n) <= 45]

        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_nums = []
        for n in nums:
            if n not in seen:
                seen.add(n)
                unique_nums.append(n)

        # Si faltan números, buscar más adelante
        if len(unique_nums) < 6:
            extra_zone = text[text.find(match.group(1)) + len(match.group(1)):text.find(match.group(1)) + 1000]
            extra_nums = re.findall(r"\b\d{1,2}\b", extra_zone)
            for n in extra_nums:
                n_int = int(n)
                if 0 <= n_int <= 45 and n_int not in seen:
                    unique_nums.append(n_int)
                    seen.add(n_int)

        # Formatear en dos dígitos
        return [f"{n:02d}" for n in unique_nums[:6]]
    return []

def parse_results(text):
    # Extraer jugadas
    tradicional = extract_section_numbers(text, "TRADICIONAL PRIMER SORTEO")
    segunda = extract_section_numbers(text, "TRADICIONAL LA SEGUNDA DEL QUINI")
    revancha = extract_section_numbers(text, "REVANCHA")
    siempre_sale = extract_section_numbers(text, "SIEMPRE SALE")

    def aciertos(jugada):
        return len(set(int(n) for n in jugada) & set(MY_NUMBERS))

    message = f"""
📢 QUINI 6 - RESULTADOS OCR
🎯 Tradicional: {' – '.join(tradicional) if tradicional else 'N/D'} ✅ Aciertos: {aciertos(tradicional)}
🎯 La Segunda: {' – '.join(segunda) if segunda else 'N/D'} ✅ Aciertos: {aciertos(segunda)}
🎯 Revancha: {' – '.join(revancha) if revancha else 'N/D'} ✅ Aciertos: {aciertos(revancha)}
🎯 Siempre Sale: {' – '.join(siempre_sale) if siempre_sale else 'N/D'} ✅ Aciertos: {aciertos(siempre_sale)}

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

