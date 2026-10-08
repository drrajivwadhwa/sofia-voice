# SOFIA's voice: Kokoro v1.0, free and open (Apache 2.0); smaller int8 model file so it fits a free 512 MB computer.
# Clip N is Dr. Wadhwa's choice (2026-10-07). Recipe: docs/sofia/voice/VOICE-N-RECIPE.md in bpm-home.
import io, subprocess, threading
import numpy as np, soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from kokoro_onnx import Kokoro

k = Kokoro("kokoro.onnx", "voices.bin")
g = k.get_voice_style
e, h, i, s = g("bf_emma"), g("af_heart"), g("bf_isabella"), g("af_sarah")
H = e * 0.6 + h * 0.4
J = i * 0.65 + s * 0.35
C = h
VOICES = {"N": (J + C) / 2, "L": (H + C) / 2, "M": (H + J) / 2, "K": (H + J + C) / 3, "H": H, "J": J, "C": C}
lock = threading.Lock()  # one voice at a time on the small free computer
app = FastAPI()

class Ask(BaseModel):
    text: str
    voice: str = "N"
    speed: float = 0.96

@app.get("/health")
def health():
    return {"ok": True, "voices": list(VOICES)}

@app.post("/speak")
def speak(a: Ask):
    text = " ".join(a.text.split())[:600]
    if not text:
        raise HTTPException(400, "nothing to say")
    style = VOICES.get(a.voice.upper(), VOICES["N"])
    speed = min(max(a.speed, 0.8), 1.2)
    with lock:
        samples, sr = k.create(text, voice=style, speed=speed, lang="en-us")
    wav = io.BytesIO()
    sf.write(wav, samples, sr, format="WAV")
    mp3 = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-ac", "1", "-b:a", "48k", "-f", "mp3", "pipe:1"],
                         input=wav.getvalue(), capture_output=True, check=True).stdout
    return Response(mp3, media_type="audio/mpeg", headers={"cache-control": "no-store"})
