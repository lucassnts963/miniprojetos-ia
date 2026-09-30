"""Sincroniza a narração (parte01/02.mp3) com as cenas do render.py.

Gera:
  timing.json  -> duração de cada cena + momentos (cues) em segundos relativos ao início da cena
  segments     -> onde cortar cada áudio e onde colocar na linha do tempo
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(HERE, "words.json"), encoding="utf-8"))

LEAD = 0.55   # fala começa depois do fade-in da cena
TAIL = 0.9    # respiro depois da última palavra antes de trocar de cena

# (cena, parte, âncora de início, duração mínima, {cue: âncora})
PLAN = [
    ("hook", "parte01", "essa cobrinha", 8.0, {}),
    ("titulo", "parte01", "neuro evolução", 4.0, {}),
    ("roteiro", "parte01", "hoje eu vou", 6.0, {}),
    ("estrutura", "parte01", "o projeto é pequeno", 12.0,
     {"hl": "todo cérebro mora", "flow": "detalhe importante"}),
    ("sensores", "parte01", "mas o que a cobra", 14.0,
     {"n1": "ela recebe 11", "perigo": "primeiro três sensores", "direcao": "depois para onde",
      "comida": "por último onde", "relativo": "e como tudo"}),
    ("cerebro", "parte01", "agora o cérebro", 14.0,
     {"init": "onze entradas", "forward": "e três saídas", "params": "somando tudo", "mut": "quem ajusta"}),
    ("evolucao", "parte01", "como ela aprende", 12.0, {}),
    ("evolucao_codigo", "parte01", "no código todo", 12.0,
     {"aval": "no código todo", "elite": "os 10", "filhos": "os filhos vêm", "cross": "misturados peso"}),
    ("fitness", "parte01", "e quem decide", 12.0,
     {"prof": "ela é o professor", "comer": "comer vale", "shaping": "chegar perto", "fome": "e quem fica rodando"}),
    ("treino", "parte01", "esse aqui é o treino", 22.0,
     {"n1": "o painel mostra", "caos": "no começo é", "estrategia": "aos poucos", "fim": "e no final"}),
    ("mente", "parte02", "agora a parte", 56.0,
     {"sensores": "os quadradinhos", "pesos": "na direita cada", "comida": "repara quando", "perigo": "e quando surge",
      "fast": "agora na velocidade"}),
    ("jogo_real", "parte02", "para plugar", 12.0,
     {"conv": "a função decide", "mesmo": "ela treinou", "game": "e como o jogo"}),
    ("rodar", "parte02", "quer testar", 9.0, {}),
    ("aplicacoes", "parte02", "e fora do jogo", 11.0, {}),
    ("outro", "parte02", "como eu sempre", 7.0, {}),
]


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]", "", w)


TOK = {k: [(s, e, norm(w)) for s, e, w in v["words"] if norm(w)] for k, v in W.items()}


def find(part, phrase, after=0.0):
    want = [norm(x) for x in phrase.split()]
    toks = TOK[part]
    for i in range(len(toks) - len(want) + 1):
        if toks[i][0] < after - 0.01:
            continue
        if all(toks[i + j][2].startswith(want[j]) or want[j].startswith(toks[i + j][2]) for j in range(len(want))):
            return i
    sys.exit(f"âncora não encontrada: {part} '{phrase}' depois de {after}")


# índice da primeira palavra de cada cena
starts = []
cursor = {"parte01": 0.0, "parte02": 0.0}
for name, part, anchor, _, _ in PLAN:
    i = find(part, anchor, cursor[part])
    starts.append(i)
    cursor[part] = TOK[part][i][0]

timing, segments, t_scene = {}, [], 0.0
for k, (name, part, anchor, mind, cues) in enumerate(PLAN):
    toks = TOK[part]
    i0 = starts[k]
    nxt = next((starts[j] for j in range(k + 1, len(PLAN)) if PLAN[j][1] == part), None)
    i1 = (nxt - 1) if nxt is not None else len(toks) - 1
    w0, w1 = toks[i0][0], toks[i1][1]
    # corte no meio do silêncio entre cenas (sem comer sílaba)
    cut_a = w0 - min(0.12, (w0 - toks[i0 - 1][1]) / 2) if i0 > 0 else 0.0
    cut_b = w1 + min(0.25, (toks[i1 + 1][0] - w1) / 2) if i1 + 1 < len(toks) else W[part]["duration"]
    speech = w1 - w0
    dur = round(max(mind, LEAD + speech + TAIL), 2)
    cue_t = {}
    for cname, cphrase in cues.items():
        ci = find(part, cphrase, w0)
        cue_t[cname] = round(LEAD + toks[ci][0] - w0, 2)
    timing[name] = dict(dur=dur, start=round(t_scene, 2), cues=cue_t, speech=round(speech, 2))
    segments.append(dict(scene=name, part=part, a=round(cut_a, 3), b=round(cut_b, 3),
                         at=round(t_scene + LEAD - (w0 - cut_a), 3)))
    t_scene += dur

json.dump(dict(scenes=timing, segments=segments, total=round(t_scene, 2)),
          open(os.path.join(HERE, "timing.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for name, v in timing.items():
    m, s = divmod(v["start"], 60)
    print(f"{int(m)}:{s:05.2f}  {name:<16} cena {v['dur']:6.2f}s  fala {v['speech']:6.2f}s  cues {v['cues']}")
print("total", round(t_scene, 2))
