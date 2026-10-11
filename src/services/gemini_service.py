import logging
from typing import Optional
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

