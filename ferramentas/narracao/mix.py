"""Monta narração (cortada por cena e posicionada) + música com ducking -> narr_mix.m4a"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.join(HERE, "..", "music")
T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
total = T["total"]
segs = T["segments"]

inputs = ["-i", "C:/dev/snake/demo/parte01.mp3", "-i", "C:/dev/snake/demo/parte02.mp3",
          "-i", os.path.join(MUSIC, "tranquil_mindscape.mp3"), "-i", os.path.join(MUSIC, "lucid.mp3")]
n1 = sum(1 for s in segs if s["part"] == "parte01")
n2 = len(segs) - n1
fc = f"[0:a]aresample=48000,asplit={n1}" + "".join(f"[p1_{i}]" for i in range(n1)) + ";"
fc += f"[1:a]aresample=48000,asplit={n2}" + "".join(f"[p2_{i}]" for i in range(n2)) + ";"
labels, c1, c2 = [], 0, 0
for k, s in enumerate(segs):
    if s["part"] == "parte01":
        src, c1 = f"p1_{c1}", c1 + 1
    else:
        src, c2 = f"p2_{c2}", c2 + 1
    ms = int(round(s["at"] * 1000))
    fc += (f"[{src}]atrim={s['a']}:{s['b']},asetpts=PTS-STARTPTS,"
           f"afade=t=in:d=0.03,afade=t=out:st={s['b'] - s['a'] - 0.05:.3f}:d=0.05,adelay={ms}|{ms}[n{k}];")
    labels.append(f"[n{k}]")
fc += ("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
       f"apad=whole_dur={total},atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,asplit=2[narr][key];")
fc += (f"[2:a]atrim=0:150,aresample=48000[m1];[3:a]atrim=0:141,aresample=48000[m2];[m1][m2]acrossfade=d=4,"
       f"atrim=0:{total},asetpts=PTS-STARTPTS,afade=t=in:d=1.5,afade=t=out:st={total - 4}:d=4,"
       f"loudnorm=I=-27:TP=-3:LRA=11,aresample=48000[mus];")
fc += "[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500:makeup=1[duck];"
fc += "[narr][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95[out]"
out = os.path.join(HERE, "narr_mix.m4a")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]",
                "-c:a", "aac", "-b:a", "192k", out], check=True)
print("OK", out, total)
