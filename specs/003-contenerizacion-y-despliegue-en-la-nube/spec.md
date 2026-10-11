# Spec 003 — Contenerización y Despliegue en la Nube
Estado: implementada

## Contexto y objetivo
Actualmente el chatbot depende de ejecutarse en el entorno local del desarrollador y de túneles temporales hacia Internet (Cloudflare Tunnel). El objetivo de esta especificación es empaquetar la aplicación completa con sus dependencias de Python y del sistema operativo (en particular `ffmpeg`) dentro de un contenedor Docker reproducible, versionar el proyecto en GitHub y desplegarlo en Render (Free Tier) como un Web Service accesible 24/7 con su propio dominio HTTPS público.

## Usuarios
- Desarrolladores y administradores del sistema que requieren desplegar y mantener el servicio en la nube sin dependencias locales.
- Usuarios finales de WhatsApp que interactúan con el bot de forma continua sin interrupciones por apagado del equipo local.

## Historias de usuario
- HU-1. Como administrador del sistema, quiero empaquetar el chatbot en una imagen Docker que incluya `ffmpeg` y Python para garantizar que la transcodificación de audio funcione idénticamente en cualquier entorno.
- HU-2. Como desarrollador, quiero alojar el código en GitHub para tener trazabilidad, control de versiones y despliegue continuo hacia Render.
- HU-3. Como administrador del sistema, quiero desplegar el contenedor en Render y configurar las variables de entorno para que el webhook de WhatsApp funcione bajo un dominio seguro HTTPS permanente.

## Definiciones
- **Dockerfile**: Manifiesto declarativo que define el sistema operativo base, dependencias de sistema (`ffmpeg`), dependencias de Python y el comando de arranque del servidor.
- **Render Web Service**: Plataforma en la nube que compila y ejecuta contenedores Docker en su capa gratuita exponiendo automáticamente un puerto HTTP/HTTPS.
- **Variables de Entorno en Producción**: Parámetros de configuración sensibles (`WHATSAPP_TOKEN`, `VERIFY_TOKEN`, `PHONE_NUMBER_ID`, `GEMINI_API_KEY`) inyectados de forma segura en Render sin exponerlos en el repositorio.

## Requisitos funcionales
- RF-1: EL SISTEMA debe definir un `Dockerfile` optimizado y basado en Python 3.11+ que instale el binario de sistema `ffmpeg` mediante el gestor de paquetes de la distribución antes de instalar `requirements.txt`.
- RF-2: EL SISTEMA debe definir un archivo `.dockerignore` para excluir entornos virtuales, archivos de configuración local (`.env`), cachés y archivos temporales del contenedor.
- RF-3: EL SISTEMA debe exponer el puerto configurado (leído de la variable `PORT`, por defecto 8000 o 10000 asignado por Render) y ejecutar la aplicación mediante Uvicorn.
- RF-4: CUANDO el contenedor se inicie en Render, EL SISTEMA debe responder exitosamente con HTTP 200 en la ruta `/health`.
- RF-5: EL SISTEMA debe versionar todo el código fuente en un repositorio Git y prepararlo para sincronización con GitHub.
- RF-6: CUANDO el servicio esté desplegado en Render con su URL pública, EL SISTEMA debe permitir la verificación del Webhook de Meta (`GET /webhook`) y la recepción de eventos (`POST /webhook`).

## Requisitos no funcionales
- RNF-1: **Seguridad estricta**: El archivo `.env` y cualquier credencial real jamás deben incluirse en la imagen Docker ni subirse al repositorio de GitHub (garantizado por `.gitignore` y `.dockerignore`).
- RNF-2: **Arranque rápido**: La imagen Docker debe optimizar el tamaño de capas separando la instalación de dependencias del sistema y código fuente.
- RNF-3: **Compatibilidad con Render**: La aplicación debe vincularse a `0.0.0.0` y al puerto definido por la variable de entorno `$PORT` que asigna Render dinámicamente.

## Casos límite
- Render asigna un puerto dinámico diferente a 8000 mediante la variable de entorno `PORT`: El comando de inicio del contenedor debe respetar `${PORT:-8000}`.
- Solicitud de ping de UptimeRobot hacia `/health` en modo ahorro de energía: El endpoint `/health` debe responder con HTTP 200 OK de manera instantánea sin consultar APIs externas.

## Fuera de alcance
- Configuración de dominios personalizados con DNS propios (se utiliza el subdominio gratuito `onrender.com`).
- Bases de datos persistentes externas (la gestión de estado conversacional persiste en memoria o en el historial contextual si aplica).

## Criterios de finalización
- `Dockerfile` y `.dockerignore` creados y validados.
- Repositorio Git local limpio, con `.env` ignorado, listo para asociar al remoto de GitHub.
- Configuración de Render documentada con las variables de entorno requeridas.
- Guía de verificación del webhook en Meta con la nueva URL de Render.

## Dudas abiertas
- Ninguna. Los requisitos están alineados con la constitución del proyecto y el stack de producción.
