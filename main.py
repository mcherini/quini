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
        r = requests.get(PDF_URL, timeout=20)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        print(f"[ERROR] No se pudo descargar el PDF: {e}")
    return None

def extract_text_from_pdf(pdf_data):
    images = convert_from_bytes(pdf_data, dpi=200)
    full_text = ""
    for img in images:
        full_text += pytesseract.image_to_string(img, lang="spa") + "\n"
    return full_text

def find_jugada(text, section, allow_zero=False):
    idx = text.lower().find(section.lower())
    if idx == -1:
        return []
    snippet = text[idx: idx + 2000]
    nums = re.findall(r"\b\d{1,2}\b", snippet)
    result = []
    for n in nums:
        n_int = int(n)
        if allow_zero:
            if 0 <= n_int <= 45 and n_int not in result:
                result.append(n_int)
        else:
            if 1 <= n_int <= 45 and n_int not in result:
                result.append(n_int)
        if len(result) == 6:
            break
    return [f"{n:02d}" for n in result]

def parse_results(text):
    print("\n[DEBUG] TEXTO COMPLETO OCR (primeros 2000 caracteres):")
    print(text[:2000])  # Mostramos los primeros 2000 caracteres para analizar estructura

    # Extraemos jugadas
    tradicional = find_jugada(text, "TRADICIONAL PRIMER SORTEO")
    segunda = find_jugada(text, "TRADICIONAL LA SEGUNDA DEL QUINI", allow_zero=True)
    revancha = find_jugada(text, "REVANCHA")
    siempre_sale = find_jugada(text, "SIEMPRE SALE")

    # Debug específico para REVANCHA
    rev_idx = text.lower().find("revancha")
    if rev_idx != -1:
        print("\n[DEBUG] BLOQUE REVANCHA:")
        print(text[rev_idx: rev_idx + 500])

    def aciertos(jugada):
        return len(set(int(n) for n in jugada) & set(MY_NUMBERS))

    return f"""
📢 QUINI 6 - RESULTADOS OCR
🎯 Tradicional: {' – '.join(tradicional) if tradicional else 'N/D'} ✅ Aciertos: {aciertos(tradicional)}
🎯 La Segunda: {' – '.join(segunda) if segunda else 'N/D'} ✅ Aciertos: {aciertos(segunda)}
🎯 Revancha: {' – '.join(revancha) if revancha else 'N/D'} ✅ Aciertos: {aciertos(revancha)}
🎯 Siempre Sale: {' – '.join(siempre_sale) if siempre_sale else 'N/D'} ✅ Aciertos: {aciertos(siempre_sale)}

🎟️ Tu jugada: {', '.join(map(str, MY_NUMBERS))}

🔗 PDF Oficial: {PDF_URL}
"""

def main():
    print("[INFO] Descargando PDF...")
    pdf_data = download_pdf()
    if pdf_data:
        print("[INFO] OCR en proceso...")
        text = extract_text_from_pdf(pdf_data)
        print("[INFO] Analizando resultados...")
        msg = parse_results(text)
        asyncio.run(send_message(msg))
    else:
        asyncio.run(send_message("⚠️ No se pudo descargar el PDF oficial."))

if __name__ == "__main__":
    main()


