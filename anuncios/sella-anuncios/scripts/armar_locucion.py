"""Arma la locución final de cada anuncio y los tiempos de los subtítulos.

Corta las tomas de ElevenLabs (locucion/*.mp3) en frases, agrega pausas cortas
entre secciones y nivela el volumen al de los anuncios A–E (−14,9 LUFS).

Uso (desde anuncios/sella-anuncios):  python3 scripts/armar_locucion.py
Escribe public/audio/anuncio-{F,G}.wav y src/data/voz-{F,G}.json.
Requiere ffmpeg y numpy.
"""
import json
import re
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
TARGET_LUFS = -14.9

# Por anuncio: tramos (toma, desde, hasta, silencio después) en segundos.
# G empalma el gancho de la toma 3 (entonado como pregunta) con el resto de la toma 1.
ADS = {
    "F": [
        ("F-cristian-toma4", 0.0, 2.86, 0.25),   # ¿Quieres hacer crecer tu negocio, pero cada mes vendes lo mismo?
        ("F-cristian-toma4", 2.86, 5.07, 0.35),  # No es falta de ganas, es falta de un plan.
        ("F-cristian-toma4", 5.07, 11.85, 0.40), # El 84%… tres veces más probabilidades de que les funcione.
        ("F-cristian-toma4", 11.85, 15.71, 0.90),# En Sella armamos tu plan… seguimiento de clientes.
        ("F-cristian-toma4", 15.71, None, 0.60), # Entra a nuestra web… Revisamos tu caso.
    ],
    "G": [
        ("G-cristian-toma3", 0.0, 1.73, 0.30),   # ¿Sigues haciendo todo tu marketing a mano?
        ("G-cristian-toma1", 1.67, 6.25, 0.35),  # publicar… y mañana todo de nuevo.
        ("G-cristian-toma1", 6.25, 12.62, 0.40), # El 81%… a su marketing.
        ("G-cristian-toma1", 12.62, 15.09, 0.15),# Sella se encarga de todo eso por ti en un solo panel.
        ("G-cristian-toma1", 15.09, 16.51, 0.80),# Tú solo revisas los resultados.
        ("G-cristian-toma1", 16.51, None, 0.60), # Entra a nuestra web… Revisamos tu caso.
    ],
}

# Correcciones de texto para los subtítulos (whisper escribe "CELA", "PIME", etc.).
FIX = {"CELA": "SELLA", "PIME": "PYME", "DEL": "EL", "TRES": "3", "¿PUBLICAR,": "PUBLICAR,"}


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def write_stereo(path, a):
    pcm = np.repeat((np.clip(a, -1, 1) * 32767).astype(np.int16), 2)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def loudnorm(src, dst):
    """Normalización EBU R128 en dos pasadas (lineal) a TARGET_LUFS, pico máx. −1,5 dBTP."""
    base = f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11"
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", base + ":print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(out[out.rindex("{"): out.rindex("}") + 1])
    af = (f"{base}:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le",
                    str(dst)], check=True)


def refine(a, t, win=0.06):
    """Mueve el corte al punto más silencioso cercano."""
    cands = np.arange(max(0.0, t - win), t + win, 0.005)
    energy = [float(np.mean(a[max(0, int(c * SR) - 240): int(c * SR) + 240] ** 2)) for c in cands]
    return float(cands[int(np.argmin(energy))])


def fade(seg, ms=8):
    n = int(SR * ms / 1000)
    seg = seg.copy()
    if len(seg) > 2 * n:
        seg[:n] *= np.linspace(0, 1, n)
        seg[-n:] *= np.linspace(1, 0, n)
    return seg


audio = {}
for key, segments in ADS.items():
    pieces, words, cursor = [], [], 0.0
    for take, t0, t1, gap in segments:
        if take not in audio:
            audio[take] = (decode(ROOT / "locucion" / f"{take}.mp3"),
                           json.load(open(ROOT / "locucion" / f"{take}.palabras.json")))
        a, take_words = audio[take]
        s = refine(a, t0) if t0 > 0 else 0.0
        e = refine(a, t1) if t1 is not None else len(a) / SR
        pieces.append(fade(a[int(s * SR): int(e * SR)]))
        for ws, we, w in take_words:
            if s - 0.02 <= ws < e - 0.02:
                txt = w.strip().upper()
                txt = FIX.get(txt, txt)
                if txt == "%" and words:  # whisper separa el número del %
                    words[-1]["text"] += "%"
                    words[-1]["end"] = round(cursor + we - s, 3)
                    continue
                words.append(dict(text=txt, start=round(cursor + ws - s, 3), end=round(cursor + we - s, 3)))
        cursor += e - s
        pieces.append(np.zeros(int(gap * SR), np.float32))
        cursor += gap

    full = np.concatenate(pieces)
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "raw.wav"
        write_stereo(raw, full)
        loudnorm(raw, ROOT / "public" / "audio" / f"anuncio-{key}.wav")
    with open(ROOT / "src" / "data" / f"voz-{key}.json", "w") as f:
        json.dump(dict(duration=round(len(full) / SR, 3), words=words), f, ensure_ascii=False, indent=1)
    print(f"{key}: {len(full) / SR:.2f} s")
    print("   " + " ".join(f"{w['text']}@{w['start']:.2f}" for w in words))
