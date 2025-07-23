# Imagen base de Python
FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libtesseract-dev \
    && apt-get clean

# Configurar directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar el bot
CMD ["python", "main.py"]
