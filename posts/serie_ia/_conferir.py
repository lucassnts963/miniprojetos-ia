"""Uso interno: quadros de conferência de um short lado a lado.  python _conferir.py <parte> t1 t2 ...  -> _conf<parte>.png"""
import os
import subprocess
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "ferramentas", "venv-video", "Scripts", "python.exe")
parte, tempos = sys.argv[1], sys.argv[2:]
m = Image.new("RGB", (len(tempos) * 360, 640))
for i, t in enumerate(tempos):
    subprocess.run([PY, os.path.join(AQUI, "shorts.py"), parte, "--still", t], check=True)
    arq = os.path.join(AQUI, f"parte{parte}", f"_quadro_{float(t)}.png")
    m.paste(Image.open(arq).resize((360, 640)), (i * 360, 0))
    os.remove(arq)
m.save(os.path.join(AQUI, f"_conf{parte}.png"))
