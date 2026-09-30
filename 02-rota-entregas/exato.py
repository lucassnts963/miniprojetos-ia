"""Rota ótima COMPROVADA para poucas cidades (até ~60), por programação linear inteira.

    python exato.py --inicio "Belém/PA" --capitais

Formulação clássica: cada ligação entre duas cidades é uma variável 0/1, cada cidade tem duas
ligações, e toda vez que a solução forma um circuito separado ("sub-rota") entra uma restrição
proibindo aquele circuito. Quando sobra um circuito só, ele é o ótimo, com prova.
Para um caminho aberto (sem voltar), entra uma cidade fantasma a distância zero de todas, ligada
à cidade inicial: o caminho termina onde a fantasma se liga.
"""
import argparse
import itertools
import sys
import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

from genetico import matriz
from rota import achar, montar_mapa


def resolver_exato(D, inicio, volta=False, max_iter=200):
    n = len(D)
    if not volta:  # cidade fantasma
        D2 = np.zeros((n + 1, n + 1))
        D2[:n, :n] = D
        D = D2
    N = len(D)
    arestas = list(itertools.combinations(range(N), 2))
    idx = {e: k for k, e in enumerate(arestas)}
    custo = np.array([D[i, j] for i, j in arestas])
    E = len(arestas)
    grau = lil_matrix((N, E))
    for k, (i, j) in enumerate(arestas):
        grau[i, k] = grau[j, k] = 1
    restr = [LinearConstraint(grau.tocsr(), 2, 2)]
    lb, ub = np.zeros(E), np.ones(E)
    if not volta:
        lb[idx[(inicio, n)]] = 1  # a fantasma liga na cidade inicial
    cortes = 0
    for it in range(max_iter):
        res = milp(custo, constraints=restr, integrality=np.ones(E), bounds=Bounds(lb, ub))
        if not res.success:
            raise RuntimeError(res.message)
        x = res.x > 0.5
        # acha os circuitos da solução
        viz = {v: [] for v in range(N)}
        for k in np.where(x)[0]:
            i, j = arestas[k]
            viz[i].append(j)
            viz[j].append(i)
        visto, circuitos = set(), []
        for s in range(N):
            if s in visto:
                continue
            comp, pilha = [], [s]
            while pilha:
                v = pilha.pop()
                if v in visto:
                    continue
                visto.add(v)
                comp.append(v)
                pilha += viz[v]
            circuitos.append(comp)
        if len(circuitos) == 1:
            break
        for comp in circuitos:  # proíbe cada sub-rota: dentro dela no máximo |S|-1 ligações
            linha = np.zeros(E)
            for i, j in itertools.combinations(sorted(comp), 2):
                linha[idx[(i, j)]] = 1
            restr.append(LinearConstraint(linha, -np.inf, len(comp) - 1))
            cortes += 1
    # monta a ordem a partir da cidade inicial
    ordem, ant, v = [inicio], None, inicio
    while len(ordem) < N:
        nxt = [w for w in viz[v] if w != ant][0]
        ant, v = v, nxt
        ordem.append(v)
    if not volta:
        ordem = [c for c in ordem if c != n]
    return ordem, float(res.fun), it + 1, cortes


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--inicio", required=True)
    ap.add_argument("--estados", nargs="*")
    ap.add_argument("--capitais", action="store_true")
    ap.add_argument("--volta", action="store_true")
    ap.add_argument("--modo", choices=["reta", "estrada"], default="reta", help="linha reta ou pelas rodovias")
    args = ap.parse_args()
    mapa, fora = montar_mapa(args.modo, args.estados, capitais=args.capitais)
    if fora:
        print(f"sem rota por estrada (ficaram de fora): {', '.join(fora)}")
    if mapa.n > 1000:
        sys.exit(f"{mapa.n} cidades é muito para o método exato aqui; use rota.py")
    inicio = achar(mapa, args.inicio)
    t0 = time.time()
    ordem, total, iters, cortes = resolver_exato(matriz(mapa), inicio, args.volta)
    # a fantasma pode ter ficado "antes" da inicial: garante que o caminho sai da inicial
    if not args.volta and ordem[0] != inicio:
        ordem = ordem[::-1]
    print(f"ótimo comprovado: {total:,.0f} km  ({iters} rodadas, {cortes} sub-rotas proibidas, {time.time() - t0:.1f} s)")
    print(" -> ".join(mapa.nomes[c].split("/")[0] for c in ordem))
    assert abs(mapa.comprimento(ordem, args.volta) - total) < 1e-3, "rota não bate com o custo"


if __name__ == "__main__":
    main()
