import os
from typing import Optional
from gtts import gTTS

from api.conf import settings


class TTSDisabledError(RuntimeError):
    pass


def text_to_speech(text: str, filename: str = "output.mp3", lang: str = "ro") -> str:
    if not settings.TTS_ENABLED:
        raise TTSDisabledError("TTS este dezactivat (TTS_ENABLED=false).")

    if not text or not text.strip():
        raise ValueError("Textul pentru TTS este gol.")

    output_dir = "audio_output"
    os.makedirs(output_dir, exist_ok=True)

    safe_filename = filename.replace("/", "_").replace("\\", "_")
    output_path = os.path.join(output_dir, safe_filename)

    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    return output_path
