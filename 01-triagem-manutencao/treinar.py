"""Treina o modelo de triagem.

    python treinar.py          # validação cruzada (nota honesta) + treino final + salva modelo.npz
    python treinar.py --rapido # pula a validação cruzada
"""
import argparse
import json
import os
import sys

import numpy as np

from modelo import HERE, Triagem, carregar_dados
from rede import EQUIPES, PRIORIDADES, RedeTriagem
from vetorizador import Tfidf

sys.stdout.reconfigure(encoding="utf-8")

PARAMS = dict(n_oculta=32, epocas=100, lr=0.002, l2=3e-3, dropout=0.5)


def dobras(y, k, seed=0):
    """Divide em k partes mantendo a proporção de cada combinação equipe/prioridade."""
    rng = np.random.default_rng(seed)
    partes = [[] for _ in range(k)]
    for c in np.unique(y):
        idx = rng.permutation(np.where(y == c)[0])
        for i, j in enumerate(idx):
            partes[i % k].append(j)
    return [np.array(p) for p in partes]


def matriz(real, prev, nomes):
    m = np.zeros((len(nomes), len(nomes)), dtype=int)
    for r, p in zip(real, prev):
        m[r, p] += 1
    larg = max(len(n) for n in nomes)
    print(" " * (larg + 2) + " ".join(f"{n[:5]:>5}" for n in nomes) + "   <- previsto")
    for i, n in enumerate(nomes):
        print(f"  {n:<{larg}} " + " ".join(f"{v:>5}" for v in m[i]))


def validacao_cruzada(textos, ye, yp, k=5):
    textos = np.array(textos, dtype=object)
    prev_e, prev_p = np.zeros_like(ye), np.zeros_like(yp)
    for i, teste in enumerate(dobras(ye * 4 + yp, k)):
        treino = np.setdiff1d(np.arange(len(ye)), teste)
        m = Triagem.treinar(list(textos[treino]), ye[treino], yp[treino], seed=i, **PARAMS)
        pe, pp = m.probabilidades(list(textos[teste]))
        prev_e[teste], prev_p[teste] = pe.argmax(1), pp.argmax(1)
    acc_e, acc_p = (prev_e == ye).mean(), (prev_p == yp).mean()
    # errar por um nível (ALTA no lugar de URGENTE) é bem menos grave que errar por dois
    perto = (np.abs(prev_p - yp) <= 1).mean()
    print(f"\nValidação cruzada ({k} partes, cada chamado avaliado por um modelo que nunca o viu)")
    print(f"  equipe:     {acc_e:.1%}")
    print(f"  prioridade: {acc_p:.1%}  (no máximo um nível de diferença: {perto:.1%})")
    print("\nEquipe (real x previsto)")
    matriz(ye, prev_e, EQUIPES)
    print("\nPrioridade (real x previsto)")
    matriz(yp, prev_p, PRIORIDADES)
    erros = [(textos[i], EQUIPES[ye[i]], EQUIPES[prev_e[i]]) for i in np.where(prev_e != ye)[0]]
    if erros:
        print("\nErros de equipe:")
        for t, r, p in erros:
            print(f"  {t}  [{r} -> {p}]")
    return dict(acc_equipe=float(acc_e), acc_prioridade=float(acc_p), prioridade_1_nivel=float(perto))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="pula a validação cruzada")
    args = ap.parse_args()

    textos, ye, yp = carregar_dados()
    print(f"{len(textos)} chamados de exemplo")
    metricas = {} if args.rapido else validacao_cruzada(textos, ye, yp)

    # histórico de treino (perda e acerto por época) para a animação do vídeo
    historico = []

    def registrar(epoca, rede):
        pe, pp = rede.prever(X)
        historico.append(dict(
            epoca=epoca + 1, perda=round(rede.perda(X, ye, yp), 4),
            acc_equipe=round(float((pe.argmax(1) == ye).mean()), 4),
            acc_prioridade=round(float((pp.argmax(1) == yp).mean()), 4)))

    tfidf = Tfidf().fit(textos)
    X = tfidf.transform(textos)
    params = {k: v for k, v in PARAMS.items() if k != "n_oculta"}
    rede = RedeTriagem(X.shape[1], PARAMS["n_oculta"]).treinar(X, ye, yp, ao_fim_da_epoca=registrar, **params)
    modelo = Triagem(tfidf, rede)
    modelo.salvar()

    with open(os.path.join(HERE, "historico.json"), "w", encoding="utf-8") as f:
        json.dump(dict(params=PARAMS, metricas=metricas, n_termos=X.shape[1],
                       n_parametros=rede.n_parametros(), epocas=historico), f, ensure_ascii=False, indent=1)
    print(f"\nModelo final: {X.shape[1]} termos, {rede.n_parametros()} parâmetros -> modelo.npz, historico.json")


if __name__ == "__main__":
    main()
