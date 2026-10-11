# Constitución del Proyecto — Chatbot Multimodal para WhatsApp

Principios rectores y reglas inmutables del proyecto.

## 1. Principios arquitectónicos
- **Disponibilidad Continua y Bajo Costo**: La arquitectura debe operar de forma ininterrumpida en la capa gratuita de Render, apoyándose en la ruta `/health` y pings automatizados cada 14 minutos.
- **Higiene de Almacenamiento (Disco Efímero)**: El contenedor Docker corre en almacenamiento restringido. Todo archivo multimedia descargado temporalmente (audios, imágenes) debe eliminarse de inmediato tras su procesamiento.
- **Resiliencia Multimodal**: El sistema debe manejar fallos de conversión de audio (ffmpeg) o limitaciones de API de manera aislada, respondiendo con mensajes amigables al usuario en WhatsApp en lugar de colapsar el servidor.

## 2. Calidad y Pruebas
- Cada funcionalidad debe contar con pruebas automatizadas (`pytest`) antes de considerarse completa.
- Se debe simular el payload de Meta Webhooks (JSON de texto, imagen y audio) en los tests sin depender de llamadas directas a producción.
- No se da por completada una tarea con tests fallidos.

## 3. Seguridad y Privacidad
- **Cero Secretos en el Código**: Tokens de Meta (`WHATSAPP_TOKEN`, `VERIFY_TOKEN`, `PHONE_NUMBER_ID`) y la clave de Google (`GEMINI_API_KEY`) deben residir exclusivamente en variables de entorno (`.env` local y Environment Variables de Render).
- Los números de teléfono y contenidos de los usuarios no deben registrarse en texto claro en logs públicos.

## 4. Reglas del Flujo de Trabajo
- Toda nueva característica debe pasar por el flujo SDD: Spec -> Plan -> Tareas -> Implementación -> Verificación.
