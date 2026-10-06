"""Transcreve as narrações dos shorts com o tempo de cada palavra (faster-whisper).

    C:/dev/venv/Scripts/python.exe posts/serie_ia/transcrever.py   ->  parteN/narracao.json
"""
import glob
import json
import os

import torch  # noqa: F401  (carrega as DLLs do CUDA no Windows)
from faster_whisper import WhisperModel

AQUI = os.path.dirname(os.path.abspath(__file__))
try:
    modelo = WhisperModel("medium", device="cuda", compute_type="float16")
except Exception:  # noqa: BLE001
    modelo = WhisperModel("medium", device="cpu", compute_type="int8")
for mp3 in sorted(glob.glob(os.path.join(AQUI, "parte*", "narracao.mp3"))):
    segs, info = modelo.transcribe(mp3, language="pt", word_timestamps=True, vad_filter=False)
    palavras = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words]
    with open(mp3[:-4] + ".json", "w", encoding="utf-8") as f:
        json.dump(dict(duracao=info.duration, palavras=palavras), f, ensure_ascii=False)
    print(os.path.basename(os.path.dirname(mp3)), round(info.duration, 1), "s", len(palavras), "palavras", flush=True)
