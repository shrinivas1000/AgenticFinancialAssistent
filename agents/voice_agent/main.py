from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import tempfile
import io


try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

app = FastAPI(title="Voice Agent Service")

class TTSRequest(BaseModel):
    text: str
    voice_speed: int = 150  

class VoiceAgent:
    def __init__(self):
        if STT_AVAILABLE:
            self.recognizer = sr.Recognizer()
    
    def text_to_speech(self, text):
        if not TTS_AVAILABLE:
            raise Exception("TTS not available. Install gTTS: pip install gTTS")
        try:
            tts = gTTS(text=text, lang='en')
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return mp3_fp.read()
        except Exception as e:
            raise Exception(f"TTS error: {str(e)}")
    
    def speech_to_text(self, audio_file):
        if not STT_AVAILABLE:
            raise Exception("STT not available. Install SpeechRecognition: pip install SpeechRecognition")
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_file.read())
                temp_path = temp_file.name
            with sr.AudioFile(temp_path) as source:
                audio_data = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            raise Exception("Could not understand audio")
        except sr.RequestError as e:
            raise Exception(f"Speech recognition error: {str(e)}")
        except Exception as e:
            raise Exception(f"STT error: {str(e)}")
        finally:
            try:
                import os
                os.unlink(temp_path)
            except:
                pass
    
    def get_simple_tts_response(self, text):
        return {
            "text": text,
            "audio_available": False,
            "message": "Audio generation not available"
        }

voice_agent = VoiceAgent()

@app.post("/tts")
def text_to_speech(request: TTSRequest):
    try:
        if not TTS_AVAILABLE:
            return voice_agent.get_simple_tts_response(request.text)
        audio_data = voice_agent.text_to_speech(request.text)
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt")
def speech_to_text(audio: UploadFile = File(...)):
    try:
        if not STT_AVAILABLE:
            return {
                "text": "What's our risk exposure in Asia tech stocks today?",
                "confidence": 0.95,
                "message": "Using sample query - STT not available"
            }
        text = voice_agent.speech_to_text(audio.file)
        return {
            "text": text,
            "confidence": 0.95,
            "message": "Speech recognized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/capabilities")
def get_capabilities():
    return {
        "tts_available": TTS_AVAILABLE,
        "stt_available": STT_AVAILABLE,
        "supported_formats": ["wav", "mp3"] if STT_AVAILABLE else [],
        "message": "Voice processing capabilities"
    }

@app.get("/")
def root():
    return {"message": "Voice Agent Service"}

@app.get("/test-tts")
def test_tts():
    sample_text = "Your Asia tech allocation is 22% of portfolio, up from 18% yesterday."
    try:
        if TTS_AVAILABLE:
            audio_data = voice_agent.text_to_speech(sample_text)
            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type="audio/mpeg"
            )
        else:
            return {"message": "TTS test - audio generation not available"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-stt")
def test_stt():
    return {
        "sample_query": "What's our risk exposure in Asia tech stocks today?",
        "message": "Upload audio file to /stt endpoint for real speech recognition"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
