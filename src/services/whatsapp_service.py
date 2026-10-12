import os
import httpx
from typing import Dict, Any, Optional
from src.config import get_settings

META_GRAPH_API_VERSION = "v21.0"

async def send_whatsapp_text_message(to_phone_number: str, text: str) -> Dict[str, Any]:
    """
    Envía un mensaje de texto saliente a través de WhatsApp Cloud API (Meta).
    Endpoint: POST https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages
    """
    settings = get_settings()
    url = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}/{settings.PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

async def upload_media_file(file_path: str, mime_type: str = "audio/ogg; codecs=opus") -> str:
    """
    Sube un archivo multimedia a Meta Graph API y retorna el Media ID generado.
    Endpoint: POST https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/media
    """
    settings = get_settings()
    url = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}/{settings.PHONE_NUMBER_ID}/media"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"
    }

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    files = {
        "file": (os.path.basename(file_path), file_bytes, mime_type)
    }
    data = {
        "messaging_product": "whatsapp",
        "type": mime_type
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        media_id = response.json().get("id")
        if not media_id:
            raise ValueError("Meta no devolvió un ID para el archivo multimedia subido.")
        return media_id

async def send_whatsapp_audio_message(to_phone_number: str, media_id: str) -> Dict[str, Any]:
    """
    Envía una nota de voz / audio a través de WhatsApp Cloud API utilizando su Media ID.
    Endpoint: POST https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages
    """
    settings = get_settings()
    url = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}/{settings.PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_number,
        "type": "audio",
        "audio": {
            "id": media_id
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

async def send_whatsapp_image_message(
    to_phone_number: str,
    media_id: str,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envía un mensaje de tipo imagen a través de WhatsApp Cloud API utilizando su Media ID y un caption opcional.
    Endpoint: POST https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages
    """
    settings = get_settings()
    url = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}/{settings.PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    image_payload: Dict[str, Any] = {
        "id": media_id
    }
    if caption:
        image_payload["caption"] = caption

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_number,
        "type": "image",
        "image": image_payload
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

async def send_whatsapp_reaction(
    to_phone_number: str,
    message_id: str,
    emoji: str
) -> Dict[str, Any]:
    """
    Envía una reacción (emoji) sobre un mensaje específico en WhatsApp Cloud API.
    Endpoint: POST https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages
    """
    settings = get_settings()
    url = f"https://graph.facebook.com/{META_GRAPH_API_VERSION}/{settings.PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_number,
        "type": "reaction",
        "reaction": {
            "message_id": message_id,
            "emoji": emoji
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


