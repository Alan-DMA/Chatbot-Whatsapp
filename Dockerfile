# Dockerfile para Chatbot Multimodal de WhatsApp con Gemini
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y forzar buffer directo en logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar ffmpeg y dependencias de sistema requeridas para audio
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Definir directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY src/ ./src/

# Exponer el puerto asignado (por defecto 8000 para local, Render asigna $PORT)
EXPOSE 8000

# Iniciar servidor FastAPI usando Uvicorn respetando el puerto dinámico de Render
CMD ["sh", "-c", "exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
