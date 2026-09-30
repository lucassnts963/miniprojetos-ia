import json, sys, re, unicodedata
import torch  # noqa
from faster_whisper import WhisperModel
S = sys.argv[1]
m = WhisperModel("medium", device="cuda", compute_type="float16")
segs, _ = m.transcribe(S + "/narr_mix.m4a", language="pt", word_timestamps=True)
def norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]", "", w)
toks = [(w.start, norm(w.word)) for s in segs for w in s.words if norm(w.word)]
T = json.load(open(S + "/timing.json", encoding="utf-8"))
anchors = {"hook": "essa cobrinha", "titulo": "neuro", "roteiro": "hoje eu", "estrutura": "o projeto", "sensores": "mas o que",
           "cerebro": "agora o cerebro", "evolucao": "como ela aprende", "evolucao_codigo": "no codigo", "fitness": "e quem decide",
           "treino": "esse aqui", "mente": "agora a parte", "jogo_real": "para plugar", "rodar": "quer testar",
           "aplicacoes": "e fora", "outro": "como eu sempre"}
for name, ph in anchors.items():
    want = ph.split(); exp = T["scenes"][name]["start"] + 0.55
    hit = next((toks[i][0] for i in range(len(toks) - len(want)) if all(toks[i + j][1].startswith(want[j]) for j in range(len(want))) and toks[i][0] > exp - 5), None)
    print(f"{name:<16} esperado {exp:7.2f}  ouvido {hit if hit is None else round(hit, 2)}  delta {None if hit is None else round(hit - exp, 2)}")
