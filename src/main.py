import os
import tempfile
import logging
from typing import Dict, Any
from fastapi import FastAPI, Query, HTTPException, Response, status, Request
from src.config import get_settings
from src.services.gemini_service import (
    generate_gemini_text_response,
    generate_gemini_multimodal_response,
)
from src.services.whatsapp_service import (
    send_whatsapp_text_message,
    send_whatsapp_audio_message,
    upload_media_file,
)
from src.services.media_service import (
    get_media_url,
    download_media_file,
    cleanup_files,
)
from src.services.audio_service import (
    convert_ogg_to_mp3,
    convert_text_to_whatsapp_voice_note,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="WhatsApp Gemini Multimodal Chatbot",
    description="Webhook backend para WhatsApp Cloud API con Google Gemini",
    version="1.0.0"
)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Ruta para monitoreo externo (UptimeRobot) y comprobación de estado de Render."""
    return {"status": "ok", "service": "whatsapp-gemini-chatbot"}

@app.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    """Ruta ultraligera para UptimeRobot (evita modo sleep cada 14 min sin sobrecargar el servidor)."""
    return {"status": "alive"}

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Endpoint de verificación de Webhook de Meta (WhatsApp Cloud API).
    """
    settings = get_settings()

    if not hub_mode or not hub_verify_token or not hub_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing verification parameters"
        )

    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain", status_code=status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch"
    )

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def receive_webhook(request: Request) -> Dict[str, str]:
    """
    Endpoint receptor de eventos de Meta (mensajes entrantes de texto, imagen o audio).
    Procesa de forma multimodal con estricta limpieza de temporales en bloque finally.
    """
    try:
        body: Dict[str, Any] = await request.json()
    except Exception:
        return {"status": "ok"}

    entries = body.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])

            for message in messages:
                msg_type = message.get("type")
                from_phone = message.get("from")
                if not from_phone:
                    continue

                if msg_type == "text":
                    text_body = message.get("text", {}).get("body", "")
                    if text_body:
                        gemini_reply = await generate_gemini_text_response(prompt=text_body)
                        try:
                            await send_whatsapp_text_message(
                                to_phone_number=from_phone,
                                text=gemini_reply
                            )
                        except Exception as wa_err:
                            logger.error(f"Error al enviar mensaje de texto a WhatsApp: {wa_err}", exc_info=True)

                elif msg_type == "image":
                    image_data = message.get("image", {})
                    media_id = image_data.get("id")
                    caption = image_data.get("caption")

                    if media_id:
                        temp_files = []
                        try:
                            # 1. Obtener URL y descargar imagen
                            media_info = await get_media_url(media_id=media_id)
                            dl_url = media_info.get("url")
                            mime_type = media_info.get("mime_type", "image/jpeg")

                            temp_img = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                            temp_img_path = temp_img.name
                            temp_img.close()
                            temp_files.append(temp_img_path)

                            await download_media_file(media_url=dl_url, destination_path=temp_img_path)

                            # 2. Inferencia con Gemini
                            reply_text = await generate_gemini_multimodal_response(
                                file_path=temp_img_path,
                                mime_type=mime_type,
                                prompt=caption
                            )

                            # 3. Enviar respuesta por WhatsApp
                            await send_whatsapp_text_message(to_phone_number=from_phone, text=reply_text)
                        except Exception as img_err:
                            logger.error(f"Error procesando imagen de WhatsApp: {img_err}", exc_info=True)
                        finally:
                            cleanup_files(*temp_files)

                elif msg_type == "audio":
                    audio_data = message.get("audio", {})
                    media_id = audio_data.get("id")

                    if media_id:
                        temp_files = []
                        try:
                            # 1. Obtener URL y descargar nota de voz (.ogg Opus)
                            media_info = await get_media_url(media_id=media_id)
                            dl_url = media_info.get("url")

                            temp_ogg = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
                            temp_ogg_path = temp_ogg.name
                            temp_ogg.close()
                            temp_files.append(temp_ogg_path)

                            await download_media_file(media_url=dl_url, destination_path=temp_ogg_path)

                            # 2. Transcodificar a MP3 para Gemini
                            temp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                            temp_mp3_path = temp_mp3.name
                            temp_mp3.close()
                            temp_files.append(temp_mp3_path)

                            convert_ogg_to_mp3(input_path=temp_ogg_path, output_path=temp_mp3_path)

                            # 3. Inferencia de voz con Gemini
                            reply_text = await generate_gemini_multimodal_response(
                                file_path=temp_mp3_path,
                                mime_type="audio/mp3",
                                prompt="Transcribe o interpreta este audio y responde a lo solicitado de forma conversacional y concisa."
                            )

                            # 4. Convertir respuesta de texto a nota de voz OGG Opus
                            reply_ogg = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
                            reply_ogg_path = reply_ogg.name
                            reply_ogg.close()
                            temp_files.append(reply_ogg_path)

                            convert_text_to_whatsapp_voice_note(
                                text=reply_text,
                                output_ogg_path=reply_ogg_path
                            )

                            # 5. Subir a Meta y enviar nota de voz
                            uploaded_id = await upload_media_file(file_path=reply_ogg_path, mime_type="audio/ogg; codecs=opus")
                            await send_whatsapp_audio_message(to_phone_number=from_phone, media_id=uploaded_id)

                        except Exception as aud_err:
                            logger.error(f"Error procesando nota de voz de WhatsApp: {aud_err}", exc_info=True)
                            # Fallback elegante a texto si falla la nota de voz
                            try:
                                await send_whatsapp_text_message(
                                    to_phone_number=from_phone,
                                    text="Disculpa, tuve un inconveniente al generar la nota de voz, pero aquí tienes mi respuesta: " + reply_text if 'reply_text' in locals() else "Disculpa, no pude procesar tu nota de voz."
                                )
                            except Exception:
                                pass
                        finally:
                            cleanup_files(*temp_files)

    return {"status": "ok"}
