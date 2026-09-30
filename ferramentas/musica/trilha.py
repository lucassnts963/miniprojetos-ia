"""Coloca a trilha lo-fi num vídeo sem áudio (mesma receita do vídeo do LinkedIn da cobrinha).

    python trilha.py video.mp4                       # usa tranquil_mindscape.mp3, sobrescreve o vídeo
    python trilha.py video.mp4 lucid.mp3 saida.mp4

Fade-in de 1 s, fade-out de 3 s, loudness em -16 LUFS. Música: HoliznaCC0, "Public Domain Lofi" (CC0).
"""
import os
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FFMPEG = shutil.which("ffmpeg") or r"C:\programs\bin\ffmpeg.exe"


def duracao(caminho):
    r = subprocess.run([FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", caminho], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def colocar(video, faixa="tranquil_mindscape.mp3", saida=None):
    faixa = faixa if os.path.isabs(faixa) else os.path.join(AQUI, faixa)
    total = duracao(video)
    af = (f"atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1,"
          f"afade=t=out:st={max(0, total - 3):.3f}:d=3,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000")
    destino = saida or video
    tmp = os.path.join(tempfile.mkdtemp(prefix="trilha_"), os.path.basename(destino))
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", video, "-i", faixa, "-filter_complex", f"[1:a]{af}[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", tmp],
                   check=True)
    shutil.move(tmp, destino)
    print(f"OK {destino}  ({total:.1f} s, {os.path.basename(faixa)})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    colocar(*sys.argv[1:])
