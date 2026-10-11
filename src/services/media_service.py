import os
from typing import Dict, Any, Optional
import httpx
from src.config import get_settings

META_GRAPH_URL = "https://graph.facebook.com/v21.0"

async def get_media_url(media_id: str, access_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene la URL temporal y metadatos de un archivo multimedia usando su Media ID en Meta Graph API.
    """
    settings = get_settings()
    token = access_token or settings.whatsapp_token

    url = f"{META_GRAPH_URL}/{media_id}"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def download_media_file(media_url: str, destination_path: str, access_token: Optional[str] = None) -> str:
    """
    Descarga el archivo binario desde la URL temporal de Meta y lo guarda en destination_path.
    """
    settings = get_settings()
    token = access_token or settings.whatsapp_token

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(media_url, headers=headers)
        response.raise_for_status()
        
        # Asegurar directorio padre
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(response.content)

    return destination_path

def cleanup_files(*file_paths: Optional[str]) -> None:
    """
    Elimina los archivos especificados si existen en disco de manera segura.
    """
    for path in file_paths:
        if path and isinstance(path, str):
            try:
                if os.path.exists(path) and os.path.isfile(path):
                    os.remove(path)
            except OSError:
                pass
