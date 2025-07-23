import requests

urls = [
    "https://www.loteriasantafe.gov.ar/index.php?option=com_loteria&view=resultados&juego=quini6",
    "https://www.loteriasantafe.gov.ar/index.php/component/loteria/?view=resultados&type=quini6",
    "https://www.loteriasantafe.gov.ar/index.php/resultados/ajax?juego=quini6"
]

for url in urls:
    print(f"\n[INFO] Probando: {url}")
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        print(r.text[:500])  # Muestra los primeros 500 caracteres
    except Exception as e:
        print(f"[ERROR] {e}")
