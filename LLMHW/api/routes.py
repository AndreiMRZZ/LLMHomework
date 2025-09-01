import os
import tempfile

from aiohttp.web_fileresponse import FileResponse
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from Core.llm_agent import ask_agent
from Core.summary_tool import get_summary_by_title
from services.stt import transcribe_audio
from services.tts import text_to_speech, TTSDisabledError

router = APIRouter()

class RecommendationRequest(BaseModel):
    query: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/recommend")
def recommend_book(request: RecommendationRequest):
    try:
        response = ask_agent(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
def get_book_summary(title: str = Query(..., description="Titlul cărții")):
    try:
        summary = get_summary_by_title(title)
        return {"title": title, "summary": summary}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt")
def transcribe_voice(file: UploadFile = File(...)):
    tmp_path = None
    try:
        suffix = os.path.splitext(file.filename or "")[1] or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        text = transcribe_audio(tmp_path)
        return {"transcription": text}
    except RuntimeError as e:
        import traceback; traceback.print_exc()
        print("[/stt RuntimeError]", e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        import traceback; traceback.print_exc()
        print("[/stt Exception]", e)
        raise HTTPException(status_code=500, detail=f"Eroare interna STT: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except OSError: pass


@router.post("/tts")
def generate_audio(payload: RecommendationRequest):
    try:
        response = ask_agent(payload.query)
        audio_path = text_to_speech(response, filename="recommendation.mp3")
        return FileResponse(audio_path, media_type="audio/mpeg", filename="recommendation.mp3")
    except TTSDisabledError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))