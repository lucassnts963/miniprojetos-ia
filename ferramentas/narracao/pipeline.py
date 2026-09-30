"""Narração dos vídeos do YouTube, para qualquer projeto: transcrever -> sincronizar -> render -> mixar -> verificar.

Mesma lógica dos scripts do vídeo da cobrinha (tx.py, sync.py, mix.py, verify.py), sem caminhos fixos.
A pasta da narração tem os áudios do ElevenLabs (parte01.mp3, parte02.mp3, …) e um plano.json:

  {"cenas": [["hook", "parte01", "olha só eu escrevo", 6.0, {"cue": "frase dita"}], …],
   "musicas": ["tranquil_mindscape.mp3", "lucid.mp3"]}

  python pipeline.py transcrever <pasta>                   # words.json  (Python de C:/dev/venv: faster-whisper + GPU)
  python pipeline.py sincronizar <pasta>                   # timing.json (o render.py do vídeo lê este arquivo)
  python pipeline.py mixar <pasta> <video_silent.mp4> <saida.mp4>
  python pipeline.py verificar <pasta> <saida.mp4>

A cena começa quando a narração diz a âncora; os cues marcam o momento de cada frase dentro da cena.
Números falados e escritos casam ("passo dez" = "Passo 10"), porque o Whisper costuma escrever dígitos.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
MUSICAS = os.path.join(os.path.dirname(AQUI), "musica")
FFMPEG = shutil.which("ffmpeg") or r"C:\programs\bin\ffmpeg.exe"
LEAD = 0.55   # a fala começa depois do fade-in da cena
TAIL = 0.9    # respiro depois da última palavra antes de trocar de cena

NUMEROS = {"zero": "0", "um": "1", "uma": "1", "dois": "2", "duas": "2", "tres": "3", "quatro": "4", "cinco": "5",
           "seis": "6", "sete": "7", "oito": "8", "nove": "9", "dez": "10", "vinte": "20", "trinta": "30",
           "quarenta": "40", "cinquenta": "50", "sessenta": "60", "setenta": "70", "oitenta": "80",
           "noventa": "90", "cem": "100"}


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    w = re.sub(r"[^a-z0-9%]", "", w)
    return NUMEROS.get(w, w)


def _json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _partes(pasta):
    return sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(pasta, "parte*.mp3")))


def _whisper():
    import torch  # noqa: F401  (carrega as DLLs do CUDA no Windows)
    from faster_whisper import WhisperModel
    try:
        return WhisperModel("medium", device="cuda", compute_type="float16")
    except Exception:  # noqa: BLE001
        return WhisperModel("medium", device="cpu", compute_type="int8")


# ---------------- transcrever ----------------
def transcrever(pasta):
    m = _whisper()
    out = {}
    for nome in _partes(pasta):
        segs, info = m.transcribe(os.path.join(pasta, nome + ".mp3"), language="pt", word_timestamps=True,
                                  vad_filter=False)
        words = [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]
        out[nome] = dict(duration=info.duration, words=words)
        print(nome, round(info.duration, 1), "s", len(words), "palavras", flush=True)
    with open(os.path.join(pasta, "words.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)


# ---------------- sincronizar ----------------
def _achar(toks, parte, frase, depois=0.0):
    want = [norm(x) for x in frase.split()]
    for i in range(len(toks) - len(want) + 1):
        if toks[i][0] < depois - 0.01:
            continue
        if all(toks[i + j][2].startswith(want[j]) or want[j].startswith(toks[i + j][2]) for j in range(len(want))):
            return i
    sys.exit(f"âncora não encontrada: {parte} '{frase}' depois de {depois:.2f}s (confira words.json)")


def sincronizar(pasta):
    W = _json(os.path.join(pasta, "words.json"))
    plano = _json(os.path.join(pasta, "plano.json"))["cenas"]
    toks = {k: [(s, e, norm(w)) for s, e, w in v["words"] if norm(w)] for k, v in W.items()}
    inicios, cursor = [], {k: 0.0 for k in toks}
    for nome, parte, ancora, _, _ in plano:
        i = _achar(toks[parte], parte, ancora, cursor[parte])
        inicios.append(i)
        cursor[parte] = toks[parte][i][0]
    timing, segmentos, t_cena = {}, [], 0.0
    for k, (nome, parte, ancora, dmin, cues) in enumerate(plano):
        tk = toks[parte]
        i0 = inicios[k]
        prox = next((inicios[j] for j in range(k + 1, len(plano)) if plano[j][1] == parte), None)
        i1 = (prox - 1) if prox is not None else len(tk) - 1
        w0, w1 = tk[i0][0], tk[i1][1]
        # corta no meio do silêncio entre cenas (sem comer sílaba)
        corte_a = w0 - min(0.12, (w0 - tk[i0 - 1][1]) / 2) if i0 > 0 else 0.0
        corte_b = w1 + min(0.25, (tk[i1 + 1][0] - w1) / 2) if i1 + 1 < len(tk) else W[parte]["duration"]
        fala = w1 - w0
        dur = round(max(dmin, LEAD + fala + TAIL), 2)
        cue_t = {c: round(LEAD + tk[_achar(tk, parte, frase, w0)][0] - w0, 2) for c, frase in cues.items()}
        timing[nome] = dict(dur=dur, start=round(t_cena, 2), cues=cue_t, speech=round(fala, 2))
        segmentos.append(dict(scene=nome, part=parte, a=round(corte_a, 3), b=round(corte_b, 3),
                              at=round(t_cena + LEAD - (w0 - corte_a), 3)))
        t_cena += dur
    with open(os.path.join(pasta, "timing.json"), "w", encoding="utf-8") as f:
        json.dump(dict(scenes=timing, segments=segmentos, total=round(t_cena, 2)), f, ensure_ascii=False, indent=1)
    for nome, v in timing.items():
        m, s = divmod(v["start"], 60)
        print(f"{int(m)}:{s:05.2f}  {nome:<12} cena {v['dur']:6.2f}s  fala {v['speech']:6.2f}s  cues {v['cues']}")
    print("total", round(t_cena, 2))


# ---------------- mixar ----------------
def _duracao(caminho):
    r = subprocess.run([FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", caminho], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def mixar(pasta, video, saida):
    T = _json(os.path.join(pasta, "timing.json"))
    musicas = [os.path.join(MUSICAS, m) for m in _json(os.path.join(pasta, "plano.json")).get("musicas", [])]
    total, segs = T["total"], T["segments"]
    partes = sorted({s["part"] for s in segs})
    ins = []
    for p in partes:
        ins += ["-i", os.path.join(pasta, p + ".mp3")]
    for m in musicas:
        ins += ["-i", m]
    fc = ""
    rot = {}
    for ip, p in enumerate(partes):
        n = sum(1 for s in segs if s["part"] == p)
        fc += f"[{ip}:a]aresample=48000,asplit={n}" + "".join(f"[{p}_{i}]" for i in range(n)) + ";"
        rot[p] = 0
    labels = []
    for k, s in enumerate(segs):
        src = f"{s['part']}_{rot[s['part']]}"
        rot[s["part"]] += 1
        ms = int(round(s["at"] * 1000))
        fc += (f"[{src}]atrim={s['a']}:{s['b']},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,"
               f"afade=t=out:st={s['b'] - s['a'] - 0.05:.3f}:d=0.05,adelay={ms}|{ms}[n{k}];")
        labels.append(f"[n{k}]")
    fc += ("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
           f"apad=whole_dur={total},atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000")
    if not musicas:
        fc += "[out]"
    else:
        fc += ",asplit=2[narr][key];"
        # emenda as músicas com crossfade até cobrir o vídeo
        base = len(partes)
        fc += f"[{base}:a]aresample=48000[m0];"
        cur = "m0"
        for j in range(1, len(musicas)):
            fc += f"[{base + j}:a]aresample=48000[mi{j}];[{cur}][mi{j}]acrossfade=d=4[mc{j}];"
            cur = f"mc{j}"
        fc += (f"[{cur}]aloop=loop=-1:size=2147483647,atrim=0:{total},asetpts=PTS-STARTPTS,afade=t=in:d=1.5,"
               f"afade=t=out:st={total - 4}:d=4,loudnorm=I=-27:TP=-3:LRA=11,aresample=48000[mus];")
        fc += "[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500:makeup=1[duck];"
        fc += "[narr][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95[out]"
    audio = os.path.join(pasta, "narr_mix.m4a")
    subprocess.run([FFMPEG, "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[out]",
                    "-c:a", "aac", "-b:a", "192k", audio], check=True)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "copy", "-shortest", saida], check=True)
    print(f"OK {saida}  (vídeo {_duracao(video):.1f}s, narração {total:.1f}s)")


# ---------------- verificar ----------------
def verificar(pasta, video):
    m = _whisper()
    segs, _ = m.transcribe(video, language="pt", word_timestamps=True)
    toks = [(w.start, norm(w.word)) for s in segs for w in s.words if norm(w.word)]
    T = _json(os.path.join(pasta, "timing.json"))["scenes"]
    for nome, _parte, ancora, _, _ in _json(os.path.join(pasta, "plano.json"))["cenas"]:
        want = [norm(x) for x in ancora.split()]
        esp = T[nome]["start"] + LEAD
        hit = next((toks[i][0] for i in range(len(toks) - len(want))
                    if all(toks[i + j][1].startswith(want[j]) for j in range(len(want))) and toks[i][0] > esp - 5),
                   None)
        d = None if hit is None else round(hit - esp, 2)
        alerta = "" if d is not None and abs(d) < 0.4 else "  <- confira"
        print(f"{nome:<12} esperado {esp:7.2f}  ouvido {hit if hit is None else round(hit, 2)}  delta {d}{alerta}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    {"transcrever": transcrever, "sincronizar": sincronizar, "mixar": mixar, "verificar": verificar}[cmd](*args)
