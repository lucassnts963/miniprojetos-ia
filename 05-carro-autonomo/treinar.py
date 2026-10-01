"""Treina pelo terminal e guarda o melhor cérebro em cerebro.npz.

    python treinar.py --pista circuito --geracoes 30
"""
import argparse
import os
import time

import numpy as np

import cerebro
from evolucao import proxima_geracao, simular
from mundo import PISTAS, Mundo, Pista

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pista", default="circuito", choices=list(PISTAS))
    ap.add_argument("--geracoes", type=int, default=30)
    ap.add_argument("--carros", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    pista = Pista(a.pista)
    mundo = pista.montar(Mundo())
    genomas = cerebro.aleatorios(a.carros, rng)
    for g in range(1, a.geracoes + 1):
        t0 = time.time()
        metros, _ = simular(mundo, pista, genomas)
        print(f"geração {g:3d}  melhor {metros.max():6.0f} m ({metros.max() / pista.comprimento:4.1f} voltas)  "
              f"média {metros.mean():5.0f} m  {time.time() - t0:4.1f} s")
        melhor = genomas[metros.argmax()].copy()
        genomas = proxima_geracao(genomas, metros, rng)
    np.savez(os.path.join(AQUI, "cerebro.npz"), genoma=melhor, pista=a.pista)
    print("melhor cérebro salvo em cerebro.npz")


if __name__ == "__main__":
    main()
