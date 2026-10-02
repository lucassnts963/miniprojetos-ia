"""Treina os dois modelos no mesmo texto e mede os dois no trecho que nenhum viu.

    python baixar_textos.py     # uma vez
    python treinar.py           # pedaços -> contagem -> rede; salva tudo em modelo/

A medida: no texto guardado para teste, em quantas vezes o próximo pedaço certo era o primeiro palpite
(e em quantas estava entre os cinco primeiros).
"""
import argparse
import json
import os
import time

import numpy as np
import torch

from contagem import Contagem
from conversas import montar
from pedacos import Pedacos
from rede import PADRAO, Rede

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(AQUI, "modelo")


def lotes(dados, janela, n, dev, rng):
    i = rng.integers(0, len(dados) - janela - 1, n)
    x = np.stack([dados[j:j + janela] for j in i])
    y = np.stack([dados[j + 1:j + janela + 1] for j in i])
    return torch.from_numpy(x).to(dev), torch.from_numpy(y).to(dev)


@torch.no_grad()
def medir_rede(rede, teste, janela, dev, n=400):
    rede.eval()
    rng = np.random.default_rng(1)
    perda, top1, top5, total = 0.0, 0, 0, 0
    for _ in range(n // 50):
        x, y = lotes(teste, janela, 50, dev, rng)
        notas, p = rede(x, y)
        perda += p.item()
        cinco = notas.topk(5, -1).indices
        top1 += (cinco[..., 0] == y).sum().item()
        top5 += (cinco == y[..., None]).any(-1).sum().item()
        total += y.numel()
    rede.train()
    return perda / (n // 50), top1 / total, top5 / total


def medir_contagem(cont, teste, ordem, n=4000):
    rng = np.random.default_rng(1)
    top1 = top5 = 0
    for i in rng.integers(8, len(teste) - 1, n):
        p, _ = cont.proximo(teste[i - 8:i], ordem)
        cinco = np.argsort(-p)[:5]
        top1 += cinco[0] == teste[i]
        top5 += teste[i] in cinco
    return top1 / n, top5 / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passos", type=int, default=12000)
    ap.add_argument("--lote", type=int, default=64)
    a = ap.parse_args()
    os.makedirs(MODELO, exist_ok=True)
    with open(os.path.join(AQUI, "dados", "corpus.txt"), encoding="utf-8") as f:
        texto = f.read()
    corte = int(len(texto) * 0.95)                       # os 5% finais ficam guardados para o teste

    arq = os.path.join(MODELO, "pedacos.json")
    if os.path.exists(arq):
        ped = Pedacos.abrir(arq)
    else:
        t0 = time.time()
        ped = Pedacos.treinar(texto[:corte], PADRAO["vocab"])
        ped.salvar(arq)
        print(f"pedaços: {len(ped.vocab)} em {time.time() - t0:.0f} s", flush=True)
    treino = np.array(ped.codificar(texto[:corte]), np.int64)
    teste = np.array(ped.codificar(texto[corte:]), np.int64)
    print(f"treino: {len(treino):,} pedaços · teste: {len(teste):,}", flush=True)

    conversas = montar(texto[:corte])                    # a mesma base, em formato de pergunta e resposta
    np.random.default_rng(0).shuffle(conversas)
    chat = np.array(ped.codificar("".join(conversas)), np.int64)
    print(f"conversas tiradas da base: {len(conversas):,} ({len(chat):,} pedaços)", flush=True)

    cont = Contagem.treinar(treino, len(ped.vocab))
    cont.salvar(os.path.join(MODELO, "contagem.npz"))
    resultado = {"contagem": {}}
    for ordem in (1, 2, 3):
        t1, t5 = medir_contagem(cont, teste, ordem)
        resultado["contagem"][ordem] = dict(top1=round(float(t1), 4), top5=round(float(t5), 4))
        print(f"contagem (últimos {ordem}): acerta de primeira {t1:.1%} · entre os cinco {t5:.1%}", flush=True)

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    cfg = dict(PADRAO, vocab=len(ped.vocab))
    rede = Rede(**cfg).to(dev)
    print(f"rede: {sum(p.numel() for p in rede.parameters()):,} números para ajustar ({dev})", flush=True)
    opt = torch.optim.AdamW(rede.parameters(), lr=1e-3, weight_decay=0.05)
    rng = np.random.default_rng(0)
    t0 = time.time()
    for passo in range(1, a.passos + 1):
        for g in opt.param_groups:                      # aquece e depois desce em cosseno
            g["lr"] = 1e-3 * min(1, passo / 200) * (0.05 + 0.95 * 0.5 * (1 + np.cos(np.pi * passo / a.passos)))
        x, y = lotes(chat if passo % 5 == 0 else treino, cfg["janela"], a.lote, dev, rng)   # 1 lote em 5 é conversa
        with torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
            _, perda = rede(x, y)
        opt.zero_grad(set_to_none=True)
        perda.backward()
        torch.nn.utils.clip_grad_norm_(rede.parameters(), 1.0)
        opt.step()
        if passo % 500 == 0 or passo == a.passos:
            pt, t1, t5 = medir_rede(rede, teste, cfg["janela"], dev)
            print(f"passo {passo:5d}  perda treino {perda.item():.2f}  teste {pt:.2f}  de primeira {t1:.1%}  "
                  f"entre cinco {t5:.1%}  {time.time() - t0:.0f} s", flush=True)
    resultado["rede"] = dict(top1=round(t1, 4), top5=round(t5, 4), perda_teste=round(pt, 3), passos=a.passos,
                             parametros=sum(p.numel() for p in rede.parameters()))
    resultado["pedacos_treino"], resultado["pedacos_teste"] = int(len(treino)), int(len(teste))
    resultado["conversas"] = len(conversas)
    torch.save(dict(cfg=cfg, pesos=rede.state_dict()), os.path.join(MODELO, "rede.pt"))
    with open(os.path.join(MODELO, "resultado.json"), "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=1)
    print("salvo em modelo/")


if __name__ == "__main__":
    main()
