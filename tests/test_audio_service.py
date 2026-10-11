import pytest
import os
from unittest.mock import patch, MagicMock
from src.services.audio_service import convert_ogg_to_mp3

def test_convert_ogg_to_mp3_success(tmp_path):
    input_file = str(tmp_path / "audio.ogg")
    output_file = str(tmp_path / "audio.mp3")
    with open(input_file, "wb") as f:
        f.write(b"fake ogg data")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        # Simulamos que ffmpeg crea el archivo de salida
        with open(output_file, "wb") as f:
            f.write(b"fake mp3 data")

        res = convert_ogg_to_mp3(input_file, output_file)
        assert res == output_file
        assert os.path.exists(res)
        mock_run.assert_called_once()

def test_convert_ogg_to_mp3_input_not_found():
    with pytest.raises(FileNotFoundError):
        convert_ogg_to_mp3("inexistente.ogg", "salida.mp3")

def test_convert_ogg_to_mp3_ffmpeg_failure(tmp_path):
    input_file = str(tmp_path / "audio.ogg")
    output_file = str(tmp_path / "audio.mp3")
    with open(input_file, "wb") as f:
        f.write(b"fake ogg data")

    with patch("subprocess.run") as mock_run:
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd="ffmpeg")
        
        with pytest.raises(RuntimeError):
            convert_ogg_to_mp3(input_file, output_file)

def test_convert_to_ogg_opus_success(tmp_path):
    from src.services.audio_service import convert_to_ogg_opus
    input_file = str(tmp_path / "tts.mp3")
    output_file = str(tmp_path / "voice.ogg")
    with open(input_file, "wb") as f:
        f.write(b"fake mp3 data")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with open(output_file, "wb") as f:
            f.write(b"fake ogg opus data")

        res = convert_to_ogg_opus(input_file, output_file)
        assert res == output_file
        assert os.path.exists(res)
        mock_run.assert_called_once()

def test_convert_text_to_whatsapp_voice_note_success(tmp_path):
    from src.services.audio_service import convert_text_to_whatsapp_voice_note
    output_file = str(tmp_path / "voice_response.ogg")

    with patch("gtts.gTTS.save") as mock_gtts_save, \
         patch("src.services.audio_service.convert_to_ogg_opus") as mock_convert:
        mock_gtts_save.return_value = None
        mock_convert.return_value = output_file
        # Creamos el archivo destino simulando la conversion
        with open(output_file, "wb") as f:
            f.write(b"opus content")

        result = convert_text_to_whatsapp_voice_note(
            text="Hola, soy tu respuesta en audio.",
            output_ogg_path=output_file
        )

        assert result == output_file
        mock_gtts_save.assert_called_once()
        mock_convert.assert_called_once()

