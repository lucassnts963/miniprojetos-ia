"""Versão em vídeo do carrossel (1080x1350): a câmera desliza pelo painel contínuo, parando em cada quadro.

    C:/dev/venv/Scripts/python.exe posts/carrossel_llm_wiki.py     # gera o panorama
    C:/dev/venv/Scripts/python.exe posts/video_llm_wiki.py         # -> posts/carrossel_llm_wiki/video.mp4 (com trilha)
"""
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(AQUI, "carrossel_llm_wiki")
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "ferramentas", "musica"))
import trilha  # noqa: E402

FPS, LADO, ALT = 30, 1080, 1350
PARADA = [3.5, 5.5, 6.5, 7.5, 6.5, 6.5, 8.5, 5.5]     # segundos em cada quadro (mais texto, mais tempo)
PASSAGEM = 1.1                                        # segundos deslizando de um quadro para o outro
SUMIR = 0.6                                           # fade no começo e no fim

pano = np.asarray(Image.open(os.path.join(PASTA, "panorama.png")).convert("RGB"))
tempos, x = [], []                                    # posição da câmera ao longo do tempo
t = 0.0
for k, p in enumerate(PARADA):
    tempos += [t, t + p]
    x += [k * LADO, k * LADO]
    t += p + PASSAGEM
total = t - PASSAGEM


def camera(t):
    for i in range(1, len(tempos), 2):                # entre o fim de uma parada e o começo da seguinte
        if i + 1 < len(tempos) and tempos[i] <= t < tempos[i + 1]:
            k = (t - tempos[i]) / PASSAGEM
            k = k * k * (3 - 2 * k)                   # sai e chega devagar
            return x[i] + (x[i + 1] - x[i]) * k
    return float(np.interp(t, tempos, x))


saida = os.path.join(PASTA, "video.mp4")
ff = shutil.which("ffmpeg") or r"C:\programs\bin\ffmpeg.exe"
proc = subprocess.Popen([ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{LADO}x{ALT}",
                         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                         "-pix_fmt", "yuv420p", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
for n in range(int(total * FPS)):
    t = n / FPS
    cx = camera(t)
    i, frac = int(cx), cx - int(cx)
    a = pano[:, i:i + LADO].astype(np.float32)
    if frac and i + 1 + LADO <= pano.shape[1]:        # deslocamento menor que um pixel: movimento liso
        a = a * (1 - frac) + pano[:, i + 1:i + 1 + LADO] * frac
    brilho = min(1.0, t / SUMIR, (total - t) / SUMIR)
    proc.stdin.write((a * brilho).astype(np.uint8).tobytes())
proc.stdin.close()
proc.wait()
trilha.colocar(saida)
