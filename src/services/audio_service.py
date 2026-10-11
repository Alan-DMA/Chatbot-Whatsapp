import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def convert_ogg_to_mp3(input_path: str, output_path: str) -> str:
    """
    Transcodifica un archivo de audio (por ejemplo OGG Opus de WhatsApp) a formato MP3 usando ffmpeg.
    
    Args:
        input_path: Ruta al archivo de audio de entrada.
        output_path: Ruta de destino para el archivo .mp3.
        
    Returns:
        Ruta del archivo .mp3 generado.
        
    Raises:
        FileNotFoundError: Si el archivo de entrada no existe.
        RuntimeError: Si la ejecución de ffmpeg falla.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"El archivo de entrada no existe: {input_path}")
        
    cmd = [
        "ffmpeg",
        "-y",               # Sobrescribir salida si existe
        "-i", input_path,   # Archivo de entrada
        "-vn",              # Sin video
        "-acodec", "libmp3lame",
        "-ar", "44100",     # Frecuencia de muestreo estándar
        "-ac", "2",         # Estéreo
        "-b:a", "128k",     # Bitrate
        output_path
    ]
    
    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
        logger.error(f"Error convirtiendo audio con ffmpeg: {error_msg}")
        raise RuntimeError(f"Fallo en la transcodificación de audio: {error_msg}") from e
    except FileNotFoundError as e:
        logger.error("ffmpeg no está instalado o no se encuentra en el PATH del sistema.")
    return output_path

def convert_to_ogg_opus(input_path: str, output_path: str) -> str:
    """
    Transcodifica un archivo de audio (ej: .mp3 generado por TTS) a formato OGG Opus nativo de WhatsApp.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"El archivo de entrada no existe: {input_path}")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vn",
        "-c:a", "libopus",
        "-b:a", "32k",
        "-vbr", "on",
        output_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
        logger.error(f"Error convirtiendo a OGG Opus: {error_msg}")
        raise RuntimeError(f"Fallo en la conversión a Opus: {error_msg}") from e
    except FileNotFoundError as e:
        raise RuntimeError("ffmpeg no está disponible en el sistema.") from e

    return output_path

def convert_text_to_whatsapp_voice_note(text: str, output_ogg_path: str, lang: str = "es") -> str:
    """
    Sintetiza texto a voz usando gTTS y lo transcodifica a formato OGG Opus compatible con WhatsApp.
    """
    if not text or not text.strip():
        raise ValueError("El texto para sintetizar voz no puede estar vacío.")

    from gtts import gTTS
    import tempfile

    temp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_mp3_path = temp_mp3.name
    temp_mp3.close()

    try:
        tts = gTTS(text=text.strip(), lang=lang)
        tts.save(temp_mp3_path)
        convert_to_ogg_opus(temp_mp3_path, output_ogg_path)
    finally:
        if os.path.exists(temp_mp3_path):
            try:
                os.remove(temp_mp3_path)
            except OSError:
                pass

    return output_ogg_path

