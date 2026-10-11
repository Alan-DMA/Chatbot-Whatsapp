import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from src.services.media_service import (
    get_media_url,
    download_media_file,
    cleanup_files,
)

@pytest.mark.asyncio
async def test_get_media_url_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "url": "https://lookaside.fbsbx.com/whatsapp_business/attachments/123",
        "mime_type": "audio/ogg; codecs=opus",
        "id": "media_123"
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await get_media_url("media_123", access_token="token_test")
        
        assert result["url"] == "https://lookaside.fbsbx.com/whatsapp_business/attachments/123"
        assert result["mime_type"] == "audio/ogg; codecs=opus"
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_download_media_file_success(tmp_path):
    fake_content = b"fake audio or image content"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = fake_content

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        destination_path = str(tmp_path / "test_download.ogg")
        
        file_path = await download_media_file(
            media_url="https://lookaside.fbsbx.com/test",
            access_token="token_test",
            destination_path=destination_path
        )

        assert file_path == destination_path
        assert os.path.exists(destination_path)
        with open(destination_path, "rb") as f:
            assert f.read() == fake_content

def test_cleanup_files(tmp_path):
    file1 = tmp_path / "f1.tmp"
    file2 = tmp_path / "f2.tmp"
    file1.write_text("1")
    file2.write_text("2")

    assert os.path.exists(file1)
    assert os.path.exists(file2)

    cleanup_files(str(file1), str(file2), None, "ruta_inexistente.tmp")

    assert not os.path.exists(file1)
    assert not os.path.exists(file2)
