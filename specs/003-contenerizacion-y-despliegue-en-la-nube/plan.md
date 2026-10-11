# Plan Técnico — Spec 003: Contenerización y Despliegue en la Nube

## Archivos y responsabilidades
- `Dockerfile`:
  - Imagen base `python:3.11-slim` para optimizar peso y seguridad.
  - Instalación de dependencias del sistema operativo: `ffmpeg` mediante `apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*`.
  - Copia de `requirements.txt` e instalación con `pip install --no-cache-dir -r requirements.txt`.
  - Copia del código fuente (`src/`, etc.).
  - Comando de inicio con `uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}` utilizando `sh -c` para resolver `$PORT` dinámico de Render.
- `.dockerignore`:
  - Excluir `.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `tests/`, `.git/`, `.agents/`, logs y temporales.
- `.gitignore`:
  - Asegurar la exclusión obligatoria de `.env`, entornos virtuales y cachés.
- `render.yaml` (o configuración del Web Service en Render):
  - Definición del servicio como `env: docker`.
  - Documentación de variables requeridas: `WHATSAPP_TOKEN`, `VERIFY_TOKEN`, `PHONE_NUMBER_ID`, `GEMINI_API_KEY`.

## Decisiones justificadas
1. **Imagen base `python:3.11-slim`:** Ofrece un balance óptimo entre tamaño reducido de descarga en Render y compatibilidad binaria para compilar e instalar `ffmpeg` sin sobrecargar el almacenamiento efímero.
2. **Puerto dinámico con fallback:** Render asigna el puerto mediante `$PORT` (generalmente 10000). Usar `sh -c "exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"` garantiza que funcione tanto localmente (puerto 8000) como en Render sin cambiar código.
3. **Seguridad estricta:** Las variables sensibles no se hardcodean en el `Dockerfile` ni en el repositorio; se inyectan en la pestaña *Environment* de Render.
