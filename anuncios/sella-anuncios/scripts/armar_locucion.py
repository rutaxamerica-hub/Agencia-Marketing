"""Arma la locución final de cada anuncio y los tiempos de los subtítulos.

Toma de ElevenLabs (locucion/*.mp3) cortada en frases, con pausas como en los
anuncios A–E, y al final la CTA original (idéntica en A–E).

Uso (desde anuncios/sella-anuncios):  python3 scripts/armar_locucion.py
Escribe public/audio/anuncio-{F,G}.wav y src/data/voz-{F,G}.json.
Requiere ffmpeg y numpy.
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000

# Tiempos de palabra de la CTA original, relativos al inicio de locucion/cta-original.wav.
CTA_WORDS = [("ENTRA", 0.61, 1.17), ("A", 1.17, 1.23), ("NUESTRA", 1.23, 1.41), ("WEB", 1.41, 1.69),
             ("Y", 1.69, 1.89), ("AGENDA", 1.89, 2.23), ("UNA", 2.23, 2.39), ("LLAMADA", 2.39, 2.71),
             ("DE", 2.71, 2.89), ("30", 2.89, 3.25), ("MINUTOS.", 3.25, 3.67), ("REVISAMOS", 4.13, 4.63),
             ("TU", 4.63, 4.83), ("CASO.", 4.83, 5.07)]

# Por anuncio: toma elegida, cortes (segundo del corte, silencio a insertar) y correcciones de texto
# para los subtítulos (whisper escribe "CELA", "PIME", etc.).
ADS = {
    "F": dict(take="F-toma2", gap_cta=0.9,
              cuts=[(1.67, 0.20), (4.64, 0.40), (9.19, 0.0), (15.11, 0.45), (18.0, 0.10)],
              fix={"Sella,": "SELLA"}),
    "G": dict(take="G-toma1", gap_cta=0.8,
              cuts=[(2.57, 0.20), (9.19, 0.30), (13.0, 0.0), (17.70, 0.35), (24.04, 0.10)],
              fix={"CELA": "SELLA", "PIME": "PYME", "Tu": "TÚ", "¿Publicar,": "PUBLICAR,", "mañana?": "MAÑANA,"}),
}


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def write(path, a, stereo=False):
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    if stereo:
        pcm = np.repeat(pcm, 2)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2 if stereo else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def lufs(a):
    tmp = ROOT / "out" / "tmp_lufs.wav"
    tmp.parent.mkdir(exist_ok=True)
    write(tmp, a)
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    tmp.unlink()
    return float([l for l in out.splitlines() if l.strip().startswith("I:")][-1].split()[1])


def refine(a, t, win=0.09):
    """Mueve el corte al punto más silencioso cercano."""
    cands = np.arange(t - win, t + win, 0.005)
    energy = [float(np.mean(a[max(0, int(c * SR) - 240): int(c * SR) + 240] ** 2)) for c in cands]
    return float(cands[int(np.argmin(energy))])


def fade(seg, ms=8):
    n = int(SR * ms / 1000)
    seg = seg.copy()
    if len(seg) > 2 * n:
        seg[:n] *= np.linspace(0, 1, n)
        seg[-n:] *= np.linspace(1, 0, n)
    return seg


cta = decode(ROOT / "locucion" / "cta-original.wav")
cta_lufs = lufs(cta)

for key, cfg in ADS.items():
    body = decode(ROOT / "locucion" / f"{cfg['take']}.mp3")
    words = json.load(open(ROOT / "locucion" / f"{cfg['take']}.palabras.json"))
    body = body * 10 ** ((cta_lufs - lufs(body)) / 20)  # mismo volumen que la CTA original

    pieces, spans, shift, prev = [], [], 0.0, 0.0
    for t, gap in [(refine(body, t), g) for t, g in cfg["cuts"]] + [(len(body) / SR, 0.0)]:
        pieces.append(fade(body[int(prev * SR): int(t * SR)]))
        spans.append((prev, t, shift))
        if gap:
            pieces.append(np.zeros(int(gap * SR), np.float32))
            shift += gap
        prev = t

    out_words = []
    for s, e, w in words:
        sh = next(x[2] for x in spans if x[0] - 1e-6 <= s < x[1] + 1e-6)
        txt = cfg["fix"].get(w.strip(), w.strip()).upper()
        if txt == "%":  # whisper separa el número del %
            out_words[-1]["text"] += "%"
            out_words[-1]["end"] = round(e + sh, 3)
            continue
        out_words.append(dict(text=txt, start=round(s + sh, 3), end=round(e + sh, 3)))

    body_out = np.concatenate(pieces)
    t_cta = len(body_out) / SR + cfg["gap_cta"]
    full = np.concatenate([body_out, np.zeros(int(cfg["gap_cta"] * SR), np.float32), fade(cta),
                           np.zeros(int(0.6 * SR), np.float32)])
    out_words += [dict(text=w, start=round(s + t_cta, 3), end=round(e + t_cta, 3)) for w, s, e in CTA_WORDS]

    write(ROOT / "public" / "audio" / f"anuncio-{key}.wav", full, stereo=True)
    with open(ROOT / "src" / "data" / f"voz-{key}.json", "w") as f:
        json.dump(dict(duration=round(len(full) / SR, 3), ctaStart=round(t_cta, 3), words=out_words),
                  f, ensure_ascii=False, indent=1)
    print(f"{key}: {len(full) / SR:.2f} s, CTA en {t_cta:.2f} s")
