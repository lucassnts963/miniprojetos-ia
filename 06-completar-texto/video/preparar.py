"""Tira do modelo treinado os dados que o vídeo mostra (nada no vídeo é inventado à mão).

    venv/Scripts/python.exe video/preparar.py     # -> video/dados.json
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import demo  # noqa: E402

FRASE = "A manutenção preventiva é"
COMPARA = "A bomba hidráulica"
SEMENTE_PASSOS, SEMENTE_COMPARA = 3, 1        # sorteios usados no vídeo (trocar aqui muda o exemplo)

d = dict(frase=FRASE, compara=COMPARA)
d["pedacos"] = demo.proximo(dict(texto=FRASE))["pedacos"]
d["contagem"] = demo.proximo(dict(texto=FRASE, modelo="contagem", ordem=3, n=5))["apostas"]
d["passos"] = demo.gerar(dict(texto=FRASE, modelo="rede", temperatura=0.5, quantos=14, semente=SEMENTE_PASSOS))["passos"]
d["compara_pedacos"] = demo.proximo(dict(texto=COMPARA))["pedacos"]
for m in ("contagem", "rede"):
    g = demo.gerar(dict(texto=COMPARA, modelo=m, ordem=3, temperatura=0.6, quantos=30, semente=SEMENTE_COMPARA))
    d["compara_" + m] = [p["pedaco"] for p in g["passos"]]
with open(os.path.join(AQUI, "dados.json"), "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding="utf-8")
print(FRASE + "".join(p["pedaco"] for p in d["passos"]))
print("contagem:", COMPARA + "".join(d["compara_contagem"]))
print("rede:    ", COMPARA + "".join(d["compara_rede"]))
