"""Monta os timelapses (LinkedIn 1080x1080 e Stories/Reels 1080x1920) a partir de demo/snake.mp4."""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/dev/snake/demo/snake.mp4"
MUSIC = os.path.join(HERE, "music", "tranquil_mindscape.mp3")
OUT_DIR = "C:/dev/snake/demo"

TRAIN_START, TRAIN_DUR = 11, 1404       # painel de neuroevolução (gerações 1..100)
PLAY_START, PLAY_DUR = 1450, 440.6      # IA treinada jogando (score 0 -> 50)
TRAIN_CROP = "968:692:476:254"
PLAY_CROP = "500:500:710:350"

BG = "0x12121c"
GREEN = "0x50dc78"
MUTED = "0xa0a6c8"
FPS = 30

for f in ("segoeuib.ttf", "segoeui.ttf"):
    if not os.path.exists(os.path.join(HERE, f)):
        shutil.copy(f"C:/Windows/Fonts/{f}", HERE)

INICIO = "no começo: nenhuma inteligência"
ACELERA = "acelerando a evolução..."
FIM = "fim do treino: bem mais esperta"

PROFILES = {
    "linkedin": dict(
        W=1080, H=1080, play_speed=12, intro=3.0, card=2.0, outro=3.5,
        # tempo real -> rampa -> bem acelerado -> rampa -> desacelera no final
        train_segs=[(11, 23, 1, INICIO), (23, 63, 4, ACELERA), (63, 1330, 120, ACELERA),
                    (1330, 1370, 4, ACELERA), (1370, 1404, 2, FIM)],
        train_w=1000, train_y=205, play_w=740, play_y=190,
        title_y=70, sub_y=130, cap_y=940, big=64, mid=38, small=30,
    ),
    "stories": dict(
        W=1080, H=1920, play_speed=21, intro=2.3, card=1.5, outro=2.6,
        train_segs=[(11, 18, 1, INICIO), (18, 38, 4, ACELERA), (38, 1356, 220, ACELERA),
                    (1356, 1376, 4, ACELERA), (1376, 1390, 1.5, FIM)],
        train_w=1040, train_y=560, play_w=900, play_y=470,
        title_y=300, sub_y=365, cap_y=1420, big=72, mid=44, small=36,
    ),
}


def txt(name, content):
    path = os.path.join(HERE, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"{name}.txt"


def dt(textfile, size, color, y, bold=True):
    """Um drawtext por linha (o multilinha nativo do drawtext deixa espaçamento enorme)."""
    font = "segoeuib.ttf" if bold else "segoeui.ttf"
    with open(os.path.join(HERE, textfile), encoding="utf-8") as f:
        lines = f.read().split("\n")
    out = []
    for i, line in enumerate(lines):
        name = textfile.replace(".txt", f"_l{i}.txt")
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            f.write(line)
        out.append(f"drawtext=fontfile={font}:textfile={name}:fontsize={size}:fontcolor={color}:"
                   f"x=(w-text_w)/2:y={y + int(i * size * 1.3)}")
    return ",".join(out)


def run(args):
    print(" ".join(args[:6]), "...", flush=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], cwd=HERE, check=True)


ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def fades(d, fin=0.4, fout=0.4):
    return f"fade=t=in:st=0:d={fin},fade=t=out:st={d - fout:.3f}:d={fout}"


def title_card(p, name, lines, d):
    """lines: lista de (texto, tamanho, cor, y, bold)"""
    W, H = p["W"], p["H"]
    parts = [dt(txt(f"{name}_{i}", t), s, c, y, b) for i, (t, s, c, y, b) in enumerate(lines)]
    vf = ",".join(parts + [fades(d)])
    run(["-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}:d={d}", "-vf", vf, *ENC, f"{name}.mp4"])


def clip(p, name, start, dur, crop, speed, width, y, title, sub, caption, bar):
    W, H = p["W"], p["H"]
    d = dur / speed
    fc = (
        f"[0:v]crop={crop},setpts=(PTS-STARTPTS)/{speed},fps={FPS},scale={width}:-2:flags=lanczos[v];"
        f"color=c={BG}:s={W}x{H}:r={FPS}:d={d:.3f}[bg];"
        f"[bg][v]overlay=x=(W-w)/2:y={y}:shortest=1[a];"
    )
    last = "a"
    if bar:  # barra de progresso das gerações
        fc += (f"color=c={GREEN}:s={W}x10:r={FPS}:d={d:.3f}[bar];"
               f"[{last}][bar]overlay=x='-w+w*t/{d:.3f}':y={H - 10}[b];")
        last = "b"
    texts = [
        dt(txt(f"{name}_t", title), p["small"], GREEN, p["title_y"]),
        dt(txt(f"{name}_s", sub), p["mid"], "white", p["sub_y"]),
        dt(txt(f"{name}_c", caption), p["small"], MUTED, p["cap_y"], bold=False),
    ]
    fc += f"[{last}]" + ",".join(texts + [fades(d)]) + "[out]"
    run(["-ss", str(start), "-t", str(dur), "-i", SRC, "-filter_complex", fc, "-map", "[out]",
         "-t", f"{d:.3f}", *ENC, f"{name}.mp4"])
    return d


def ramp_clip(p, name, segs, crop, width, y, title, caption):
    """Treino com velocidade variável. segs: [(ini_src, fim_src, velocidade, subtítulo)].
    O subtítulo troca conforme a fase; a barra verde embaixo mostra o avanço."""
    W, H = p["W"], p["H"]
    n = len(segs)
    fc = f"[0:v]crop={crop},split={n}" + "".join(f"[s{i}]" for i in range(n)) + ";"
    t, windows = 0.0, []
    for i, (a, b, sp, sub) in enumerate(segs):
        fc += f"[s{i}]trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{sp},fps={FPS}[p{i}];"
        d = (b - a) / sp
        windows.append((t, t + d, sub))
        t += d
    d = t
    fc += "".join(f"[p{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,scale={width}:-2:flags=lanczos[v];"
    fc += (f"color=c={BG}:s={W}x{H}:r={FPS}:d={d:.3f}[bg];[bg][v]overlay=x=(W-w)/2:y={y}:shortest=1[a];"
           f"color=c={GREEN}:s={W}x10:r={FPS}:d={d:.3f}[bar];[a][bar]overlay=x='-w+w*t/{d:.3f}':y={H - 10}[b];")
    texts = [dt(txt(f"{name}_t", title), p["small"], GREEN, p["title_y"]),
             dt(txt(f"{name}_c", caption), p["small"], MUTED, p["cap_y"], bold=False)]
    merged = []  # junta fases seguidas com o mesmo subtítulo
    for w in windows:
        if merged and merged[-1][2] == w[2]:
            merged[-1] = (merged[-1][0], w[1], w[2])
        else:
            merged.append(w)
    for i, (t0, t1, sub) in enumerate(merged):
        texts.append(dt(txt(f"{name}_s{i}", sub), p["mid"], "white", p["sub_y"])
                     .replace(",drawtext", f":enable='between(t,{t0:.3f},{t1:.3f})',drawtext")
                     + f":enable='between(t,{t0:.3f},{t1:.3f})'")
    fc += "[b]" + ",".join(texts + [fades(d)]) + "[out]"
    run(["-t", str(segs[-1][1] + 1), "-i", SRC, "-filter_complex", fc, "-map", "[out]", "-t", f"{d:.3f}",
         *ENC, f"{name}.mp4"])
    print(f"  treino: {d:.1f}s -> " + ", ".join(f"{s}: {b - a:.1f}s" for a, b, s in merged))
    return d


def build(profile):
    p = PROFILES[profile]
    H = p["H"]
    pre = f"{profile}_"
    cy = H // 2
    title_card(p, pre + "intro", [
        ("INTELIGÊNCIA ARTIFICIAL NA PRÁTICA", p["small"], GREEN, cy - 150, True),
        ("Ensinei uma IA\na jogar Snake", p["big"], "white", cy - 90, True),
        ("sem regras: ela aprendeu errando e evoluindo", p["mid"] - 6, MUTED, cy + 90, False),
    ], p["intro"])

    ramp_clip(p, pre + "train", p["train_segs"], TRAIN_CROP, p["train_w"], p["train_y"],
              "1 · APRENDIZADO", "A cada rodada, as melhores tentativas\nviram a base da próxima.")

    title_card(p, pre + "card", [
        ("Depois do aprendizado...", p["big"] - 8, "white", cy - 60, True),
        ("a IA joga sozinha", p["mid"], GREEN, cy + 30, True),
    ], p["card"])

    clip(p, pre + "play", PLAY_START, PLAY_DUR, PLAY_CROP, p["play_speed"], p["play_w"], p["play_y"],
         "2 · RESULTADO", "a IA jogando sozinha",
         "Ninguém ensinou as regras:\nela aprendeu com os próprios erros.",
         bar=False)

    title_card(p, pre + "outro", [
        ("O jogo é só a demonstração.", p["mid"], MUTED, cy - 90, False),
        ("A sua imaginação\né o limite.", p["big"], "white", cy - 20, True),
    ], p["outro"])

    seq = ["intro", "train", "card", "play", "outro"]
    if profile == "linkedin":  # cena animada de aplicação industrial (gerada por sim_industry.py)
        subprocess.run([os.path.join(HERE, "yt", "venv", "Scripts", "python.exe"), "sim_industry.py"], cwd=HERE, check=True)
        seq.insert(4, "industry")
    parts = [pre + s + ".mp4" for s in seq]
    with open(os.path.join(HERE, pre + "list.txt"), "w") as f:
        f.writelines(f"file '{x}'\n" for x in parts)
    run(["-f", "concat", "-safe", "0", "-i", pre + "list.txt", "-c", "copy", pre + "video.mp4"])

    total = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", pre + "video.mp4"],
        cwd=HERE).decode().strip())
    af = (f"atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1,"
          f"afade=t=out:st={total - 3:.3f}:d=3,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000")
    out = os.path.join(OUT_DIR, f"snake_timelapse_{profile}.mp4")
    run(["-i", pre + "video.mp4", "-i", MUSIC, "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v", "-map", "[a]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", out])
    print(f"OK {out} ({total:.1f}s)")


if __name__ == "__main__":
    for prof in sys.argv[1:] or PROFILES:
        build(prof)
