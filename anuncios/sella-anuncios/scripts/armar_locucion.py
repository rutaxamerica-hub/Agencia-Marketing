"""Arma la locución final de cada anuncio y los tiempos de los subtítulos.

1. Corta las tomas de ElevenLabs (locucion/*.mp3) en tramos.
2. Desacelera sólo la voz (atempo, conserva el timbre) y agrega respiros en comas
   y puntos, únicamente donde la toma ya tiene un micro-silencio (no corta palabras).
3. Ecualiza (menos nasal en 1,6 kHz, menos siseo) y nivela a −14,9 LUFS como A–E.
4. Retranscribe el resultado con whisper para que los subtítulos calcen exacto.

Uso (desde anuncios/sella-anuncios):  python3 scripts/armar_locucion.py
Escribe public/audio/anuncio-{F,G}.wav y src/data/voz-{F,G}.json.
Requiere ffmpeg, numpy y faster-whisper.
"""
import json
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
TARGET_LUFS = -14.9
TEMPO_GANCHO = 0.88  # velocidad del gancho (1 = original)
TEMPO = 0.85  # velocidad del resto
PAUSA = {".": 0.32, "?": 0.32, ",": 0.14, ":": 0.2}  # respiros por puntuación (s)
EQ = ("highpass=f=70,equalizer=f=1600:t=o:w=1:g=-3.5,highshelf=f=9000:g=-3,deesser=i=0.35")

# Tramos por anuncio: (toma, desde, hasta, tempo, pausa después). None = hasta el final.
ADS = {
    "F": [
        ("F-cristian-gancho2", 0.0, 1.40, TEMPO_GANCHO, 0.30),   # ¿Quieres hacer crecer tu negocio?
        ("F-cristian-gancho2", 1.40, 1.69, TEMPO_GANCHO, 0.16),  # Pero…
        ("F-cristian-gancho2", 1.69, None, TEMPO_GANCHO, 0.55),  # cada mes vendes lo mismo.
        ("F-cristian-toma4", 2.86, 5.07, TEMPO, 0.50),           # No es falta de ganas, es falta de un plan.
        ("F-cristian-toma4", 5.07, 11.85, TEMPO, 0.55),          # El 84%… de que les funcione.
        ("F-cristian-toma4", 11.85, 15.71, TEMPO, 0.85),         # En Sella armamos tu plan…
        ("F-cristian-toma4", 15.71, None, TEMPO, 0.70),          # Entra a nuestra web… Revisamos tu caso.
    ],
    "G": [
        ("G-cristian-gancho2", 0.0, None, TEMPO_GANCHO, 0.40),   # ¿Sigues haciendo todo tu marketing… a mano?
        ("G-cristian-toma1", 1.67, 4.86, TEMPO, 0.22),           # publicar, responder… en un excel
        ("G-cristian-toma1", 4.86, 6.25, TEMPO, 0.50),           # y mañana todo de nuevo.
        ("G-cristian-toma1", 6.25, 9.28, TEMPO, 0.28),           # El 81%… dice estar agotado
        ("G-cristian-toma1", 9.28, 12.62, TEMPO, 0.55),          # y el 70%… a su marketing.
        ("G-cristian-toma1", 12.62, 15.09, TEMPO, 0.25),         # Sella se encarga de todo eso por ti en un solo panel.
        ("G-cristian-toma1", 15.09, 16.51, TEMPO, 0.85),         # Tú solo revisas los resultados.
        ("G-cristian-toma1", 16.51, None, TEMPO, 0.70),          # Entra a nuestra web… Revisamos tu caso.
    ],
}

# Correcciones de texto para los subtítulos (whisper escribe "CELA", "PIME", etc.).
FIX = {"CELA": "SELLA", "SELA": "SELLA", "PIME": "PYME", "PIMES": "PYMES", "DEL": "EL", "TRES": "3",
       "¿PUBLICAR,": "PUBLICAR,", "VENDEN": "VENDES", "AGENDE": "AGENDA", "DEDICAN": "DEDICA",
       "REVISAN": "REVISAS", "NUEVO?": "NUEVO."}


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def ff(a, af):
    """Pasa un tramo mono por un filtro de ffmpeg."""
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()
    out = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", af,
                          "-f", "s16le", "-ar", str(SR), "-ac", "1", "-"], input=pcm, check=True, capture_output=True).stdout
    return np.frombuffer(out, dtype=np.int16).astype(np.float32) / 32768


def write_stereo(path, a):
    pcm = np.repeat((np.clip(a, -1, 1) * 32767).astype(np.int16), 2)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def loudnorm(src, dst):
    """Normalización EBU R128 en dos pasadas (lineal), pico máx. −1,5 dBTP."""
    base = f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11"
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", base + ":print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(out[out.rindex("{"): out.rindex("}") + 1])
    af = (f"{base}:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le",
                    str(dst)], check=True)


def db(a, t, half=0.012):
    s = a[max(0, int((t - half) * SR)): int((t + half) * SR)]
    return 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9) if len(s) else 0.0


def quietest(a, lo, hi):
    cands = np.arange(lo, hi, 0.005)
    return min(cands, key=lambda c: db(a, c)) if len(cands) else lo


def phrase_cuts(a, words, s, e):
    """Puntos de respiro dentro del tramo: tras comas/puntos, sólo si hay un micro-silencio (< −35 dB)."""
    cuts = []
    for (ws, we, w), nxt in zip(words, words[1:]):
        p = w.strip()[-1:]
        if p in PAUSA and s < we < e - 0.05 and nxt[0] < e:
            c = quietest(a, we - 0.04, nxt[0] + 0.04)
            if db(a, c) < -35:
                cuts.append((c, PAUSA[p]))
    return cuts


def fade(seg, ms=6):
    n = int(SR * ms / 1000)
    seg = seg.copy()
    if len(seg) > 2 * n:
        seg[:n] *= np.linspace(0, 1, n)
        seg[-n:] *= np.linspace(1, 0, n)
    return seg


def transcribe(path):
    from faster_whisper import WhisperModel
    w = wave.open(str(path))
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)[::2] / 32768
    a16 = a[:: SR // 16000]  # 48k -> 16k (la voz ya está filtrada)
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(a16, language="es", word_timestamps=True)
    words = []
    for sg in segs:
        for wd in sg.words:
            txt = FIX.get(wd.word.strip().upper(), wd.word.strip().upper())
            if txt == "%" and words:
                words[-1]["text"] += "%"
                words[-1]["end"] = round(wd.end, 3)
                continue
            words.append(dict(text=txt, start=round(wd.start, 3), end=round(wd.end, 3)))
    return words


takes = {}
for key, segments in ADS.items():
    pieces = []
    for take, t0, t1, tempo, gap in segments:
        if take not in takes:
            takes[take] = (decode(ROOT / "locucion" / f"{take}.mp3"),
                           json.load(open(ROOT / "locucion" / f"{take}.palabras.json")))
        a, words = takes[take]
        s = quietest(a, t0 - 0.06, t0 + 0.06) if t0 > 0 else 0.0
        e = quietest(a, t1 - 0.06, t1 + 0.06) if t1 is not None else len(a) / SR
        bounds = [(s, 0.0)] + phrase_cuts(a, words, s, e) + [(e, gap)]
        for (c0, _), (c1, pause) in zip(bounds, bounds[1:]):
            chunk = a[int(c0 * SR): int(c1 * SR)]
            pieces.append(fade(ff(chunk, f"atempo={tempo}") if tempo != 1 else chunk))
            pieces.append(np.zeros(int(pause * SR), np.float32))
    voice = ff(np.concatenate(pieces), EQ)
    out = ROOT / "public" / "audio" / f"anuncio-{key}.wav"
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "raw.wav"
        write_stereo(raw, voice)
        loudnorm(raw, out)
    words = transcribe(out)
    with open(ROOT / "src" / "data" / f"voz-{key}.json", "w") as f:
        json.dump(dict(duration=round(len(voice) / SR, 3), words=words), f, ensure_ascii=False, indent=1)
    print(f"{key}: {len(voice) / SR:.2f} s")
    print("   " + " ".join(f"{w['text']}@{w['start']:.2f}" for w in words))
