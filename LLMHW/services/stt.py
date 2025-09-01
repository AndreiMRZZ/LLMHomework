import os
import shutil
import tempfile
from typing import Optional

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from faster_whisper import WhisperModel

FFMPEG_BIN = os.environ.get("FFMPEG_BIN")
if FFMPEG_BIN:
    AudioSegment.converter = FFMPEG_BIN

def _ensure_ffmpeg_available():
    if FFMPEG_BIN and os.path.isfile(FFMPEG_BIN):
        return
    if shutil.which("ffmpeg"):
        return
    raise RuntimeError(
        "eroare la ffmpeg"
    )

def convert_to_wav_mono16(src_path: str) -> str:
    _ensure_ffmpeg_available()
    try:
        audio = AudioSegment.from_file(src_path)
    except CouldntDecodeError as e:
        raise RuntimeError("Audio decode failed.") from e

    audio = audio.set_channels(1).set_frame_rate(16000)

    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    audio.export(out_path, format="wav", parameters=["-acodec", "pcm_s16le"])
    return out_path

_MODEL_DIR = os.environ.get("WHISPER_MODEL_DIR", r"C:\models\whisper-small")
_WHISPER_MODEL: Optional[WhisperModel] = None

def _get_model() -> WhisperModel:
    global _WHISPER_MODEL
    if _WHISPER_MODEL is not None:
        return _WHISPER_MODEL

    if not os.path.isdir(_MODEL_DIR):
        raise RuntimeError(
            f"Model Whisper inexistent la: '{_MODEL_DIR}'. "
        )

    device = os.environ.get("WHISPER_DEVICE", "cpu")
    compute = "int8" if device == "cpu" else "float16"

    try:
        print(f"[STT] Loading Whisper from local dir: '{_MODEL_DIR}' (device={device}, compute_type={compute})")
        _WHISPER_MODEL = WhisperModel(
            _MODEL_DIR,
            device=device,
            compute_type=compute
        )
        print("[STT] Whisper loaded OK.")
    except Exception as e:
        raise RuntimeError(f"Eroare la incarcarea modelului Whisper din '{_MODEL_DIR}': {e}")

    return _WHISPER_MODEL

def transcribe_audio(file_path: str, lang: str = "ro") -> str:
    wav_path = None
    try:
        wav_path = convert_to_wav_mono16(file_path)
        model = _get_model()

        segments, info = model.transcribe(
            wav_path,
            language=lang,  # pentru auto-detect pune None
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=300),
            beam_size=5
        )

        parts = []
        for seg in segments:
            if seg.text:
                parts.append(seg.text.strip())
        return " ".join(parts)

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Eroare STT offline: {e}") from e
    finally:
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass
