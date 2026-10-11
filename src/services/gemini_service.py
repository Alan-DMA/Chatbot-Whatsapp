import json
import logging
from typing import Optional, Dict, Any
from google import genai
from src.config import get_settings

logger = logging.getLogger(__name__)

def get_genai_client() -> genai.Client:
    """Instancia y retorna el cliente oficial de Google GenAI SDK con la API key."""
    settings = get_settings()
    return genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_gemini_text_response(
    prompt: str,
    model: str = "gemini-2.5-flash",
    fallback_message: Optional[str] = None
) -> str:
    """
    Genera una respuesta de texto utilizando Google Gemini de forma asíncrona.
    Maneja excepciones de forma resiliente para evitar la caída del bot.
    """
    if not prompt or not prompt.strip():
        return "No recibí ningún mensaje de texto para procesar."

    default_fallback = "Lo siento, en este momento tuve una dificultad técnica para procesar tu consulta. Por favor, intenta de nuevo en unos minutos."
    error_response = fallback_message or default_fallback

    try:
        client = get_genai_client()
        # Llamada asíncrona mediante client.aio
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt.strip()
        )
        if response and response.text:
            return response.text.strip()
        return error_response
    except Exception as exc:
        logger.error(f"Error al generar contenido con Gemini ({model}): {exc}", exc_info=True)
        return error_response

async def generate_gemini_multimodal_response(
    file_path: str,
    mime_type: str,
    prompt: Optional[str] = None,
    model: str = "gemini-2.5-flash",
    fallback_message: Optional[str] = None
) -> str:
    """
    Genera una respuesta utilizando Google Gemini recibiendo un archivo multimedia (imagen o audio) y un prompt.
    """
    default_prompt = "Por favor analiza este contenido y responde a las preguntas o detalles relevantes."
    effective_prompt = prompt.strip() if prompt and prompt.strip() else default_prompt

    default_fallback = "Lo siento, tuve un problema al procesar este archivo multimedia. Por favor, intenta de nuevo."
    error_response = fallback_message or default_fallback

    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        client = get_genai_client()
        part = genai.types.Part.from_bytes(data=file_bytes, mime_type=mime_type)

        response = await client.aio.models.generate_content(
            model=model,
            contents=[part, effective_prompt]
        )
        if response and response.text:
            return response.text.strip()
        return error_response
    except Exception as exc:
        logger.error(f"Error en inferencia multimodal de Gemini ({model}): {exc}", exc_info=True)
        return error_response

async def generate_gemini_image(
    prompt: str,
    model: str = "imagen-3.0-generate-002"
) -> bytes:
    """
    Sintetiza una imagen a partir de un prompt descriptivo utilizando el modelo Imagen de Google GenAI SDK.
    Retorna los bytes de la imagen generada.
    Lanza una excepción si la API falla o no devuelve imágenes.
    """
    if not prompt or not prompt.strip():
        raise ValueError("El prompt para generar la imagen no puede estar vacío.")

    client = get_genai_client()
    response = await client.aio.models.generate_images(
        model=model,
        prompt=prompt.strip(),
        config=genai.types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/jpeg"
        )
    )

    if not response:
        raise ValueError("El modelo de IA no devolvió respuesta.")

    images = getattr(response, "generated_images", None) or getattr(response, "images", None)
    if not images:
        raise ValueError("El modelo de IA no generó ninguna imagen.")

    img_obj = images[0]
    if hasattr(img_obj, "image") and getattr(img_obj.image, "image_bytes", None):
        return img_obj.image.image_bytes
    elif hasattr(img_obj, "image_bytes") and img_obj.image_bytes:
        return img_obj.image_bytes

    raise ValueError("No se pudieron extraer los bytes de la imagen generada.")

async def process_user_message_intent(
    text: str,
    model: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Analiza el mensaje del usuario para detectar si solicita la creación/dibujo de una imagen
    o si es un mensaje de diálogo estándar.
    Retorna un diccionario estructurado:
      - Para imagen: {"generate_image": True, "image_prompt": "...", "caption": "..."}
      - Para chat normal: {"generate_image": False, "reply": "..."}
    """
    if not text or not text.strip():
        return {
            "generate_image": False,
            "reply": "No recibí ningún mensaje de texto para procesar."
        }

    system_instruction = (
        "Eres el asistente multimodal inteligente de WhatsApp. Analiza el mensaje del usuario.\n"
        "Determina si el usuario está solicitando explícitamente crear, dibujar, generar o ilustrar una imagen, "
        "o si está seleccionando/confirmando una opción visual propuesta anteriormente (ej. 'la opción 2', 'la primera').\n\n"
        "Responde OBLIGATORIAMENTE con un único objeto JSON válido con una de las siguientes dos estructuras:\n\n"
        "1. Si el usuario QUIERE generar/dibujar una imagen:\n"
        "{\n"
        '  "generate_image": true,\n'
        '  "image_prompt": "Descripción visual detallada en inglés optimizada para un modelo generador de imágenes como Imagen 3",\n'
        '  "caption": "Mensaje breve, cordial y natural en español para acompañar la imagen en WhatsApp"\n'
        "}\n\n"
        "2. Si el usuario NO está pidiendo una imagen (conversación general, dudas, asistencia, etc.):\n"
        "{\n"
        '  "generate_image": false,\n'
        '  "reply": "Tu respuesta conversacional útil, amable y directa en español"\n'
        "}\n\n"
        "IMPORTANTE: No añadas texto explicativo fuera del JSON ni bloques markdown que impidan el parseo."
    )

    client = get_genai_client()
    raw_text = ""
    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=f"{system_instruction}\n\nMensaje del usuario:\n{text.strip()}"
        )
        raw_text = response.text.strip() if response and response.text else ""

        clean_text = raw_text
        if clean_text.startswith("```"):
            lines = clean_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_text = "\n".join(lines).strip()

        data = json.loads(clean_text)
        if isinstance(data, dict):
            if data.get("generate_image") is True:
                return {
                    "generate_image": True,
                    "image_prompt": data.get("image_prompt", text.strip()),
                    "caption": data.get("caption", "¡Aquí tienes tu imagen generada!")
                }
            elif "reply" in data:
                return {
                    "generate_image": False,
                    "reply": str(data["reply"]).strip()
                }
    except Exception as exc:
        logger.warning(f"No se pudo parsear la intención como JSON ({exc}). Usando fallback conversacional.")

    fallback_reply = raw_text if raw_text else "Hola, ¿en qué puedo ayudarte hoy?"
    return {
        "generate_image": False,
        "reply": fallback_reply
    }

